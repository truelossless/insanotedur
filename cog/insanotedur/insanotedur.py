"""Cog pour Insanotedur"""

import re
import random
import datetime
import logging
import asyncio

from redbot.core import checks, commands, Config
from redbot.core.utils import log as _log
from pyppeteer import launch
from bs4 import BeautifulSoup

# On fait correspondre le niveau de log avec celui de redbot (y'a surement plus simple mais bon)
log = logging.getLogger('insanotedur')
log.setLevel(_log.getEffectiveLevel())


class Insanotedur(commands.Cog):
    """Cog pour Insanotedur """

    def set_interval(self, func):
        """Appelle une fonction toutes les x secondes à la Javascript"""

        def aux():
            # This task gets called soon
            self._loop.create_task(func())
            # And this loops
            self.set_interval(func)

        # This bit here does a proper call to `call_later` by
        # giving it a synchronised callback, and the handle returned
        # actually works when you try and cancel it. Has we tried to
        # give this a method to create a task, it would crash the
        # canceling mechanism with `NoneType` errors, because
        # that task creation would not be a proper callback.
        self.next_tick = self._loop.call_later(self.frequency, aux)

    async def close(self):
        try:
            self.next_tick.cancel()
            log.info("Cancelled next event loop.")
        except AttributeError:
            log.info("Loop handle was None. Skipped.")
        except asyncio.CancelledError:
            log.info("Loop handle was already cancelled…")

        try:
            await self.browser.close()
            log.info("Browser closed")
        except asyncio.exceptions.InvalidStateError:
            log.error("AsyncIO Invalid State upon closing browser")

    def cog_unload(self):
        task = self._loop.create_task(self.close())

    @classmethod
    async def create(cls, bot):
        """Remplace la fonction init qui ne peut pas être async"""

        obj = cls.__new__(cls)
        super(commands.Cog, obj).__init__()

        obj._loop = asyncio.get_event_loop()
        obj.next_tick = None

        obj.bot = bot

        # tableau associatif qui va contenir si une note est présente ou pas
        obj.marks_map = {}

        obj.browser = await launch()
        obj.page = await obj.browser.newPage()
        obj.config = Config.get_conf(obj, identifier=3031688555)

        # config par défaut
        default_global = {
            'username': '',
            'password': '',
            'frequency': 60,
        }
        obj.config.register_global(**default_global)

        # cache en mémoire de la config pour avoir des accès plus faciles / rapides
        obj.username = await obj.config.username()
        obj.password = await obj.config.password()
        obj.frequency = await obj.config.frequency()

        # initialisation des notes déjà présentes
        await obj.scrape(True)
        log.info(
            'Initialisation terminée.\nRecherche de nouvelles notes toutes les %s s.', obj.frequency)

        obj.set_interval(obj.should_scrape)
        return obj

    async def should_scrape(self):
        """Vérifie si on doit à nouveau scrapper la page"""

        date = datetime.datetime.today()

        if date.weekday() == 5 or date.weekday() == 6:
            log.debug('Requête annulée: week-end.')
            return

        if date.hour >= 18 or date.hour < 8:
            log.debug('Requête annulée: nuit')
            return

        log.debug('Nouvelle requête commencée.')
        await self.scrape()
        log.debug('Requête terminée.')

    async def scrape(self, init=False):
        """Scrappe la page des notes"""

        if not self.username or not self.password:
            log.error("Nom d'utilisateur / mot de passe non spécifié !")
            return

        try:
            # Connexion au CAS avec les identifiants
            await self.page.goto('https://cas.insa-rennes.fr/cas/login?service=https://cas.insa-rennes.fr/cas/logout')
            await self.page.goto('https://cas.insa-rennes.fr/cas/login?service=https://ent.insa-rennes.fr/uPortal/Login%3FrefUrl%3D%2FuPortal%2Ff%2Finfosperso%2Fp%2FdossierAdmEtu.u19l1n17%2Fmax%2Frender.uP%253FpCp')
            await self.page.type('#username', self.username)
            await self.page.type('#password', self.password)
            await self.page.keyboard.press('Enter')
            await self.page.waitForNavigation()
        except Exception:
            # des erreurs de navigations se produiront sûrement
            log.warning('[catch] La page n\'a pas répondu.')
            return

        try:
            element = await self.page.querySelector('#portlet-DossierAdmEtu-tab2 table')
            table = await self.page.evaluate('element => element.outerHTML', element)
        except Exception:
            log.warning('[catch] La page HTML est mal formée.')
            log.warning('Les identifiants sont-ils corrects ?')
            return

        soup = BeautifulSoup(table, 'html.parser')

        # on boucle sur chaque ligne (nom_note, note)
        for el in soup.find_all('tr', attrs={'style': 'border-bottom: 0.1em solid #B6CBD6'}):

            # nom de la matière
            topic = el.find('td', attrs={'align': 'left'}).text.strip()
            topic = re.compile(r"-(.*)").search(topic)[1]

            # on vérifie si une note est présente
            mark = el.find('td', attrs={'align': 'right'}).text
            mark_submitted = bool(re.compile(
                r"[,0-9]+ \/ [0-9]{2}").search(mark))

            # pendant l'initialisation on enregistre les notes dans la table associative sans broadcast
            if init:
                self.marks_map[topic] = mark_submitted
                if mark_submitted:
                    log.info('Note existante pour {}'.format(topic))

            # nouvelle note disponible, il faut informer les serveurs
            elif not self.marks_map[topic] and mark_submitted:
                emojis = ['😱', '😳', '😌', '🤕', '😇', '🤠', '😐']
                # Première chaine sans le ping
                yeet = 'Nouvelle note pour: {} {}\n'.format(
                    topic, random.choice(emojis))
                self.marks_map[topic] = True
                log.info(yeet)
                # J'ai besoin d'avoir accès au contexte du canal…
                for guild in self.bot.guilds:
                    for channel in guild.channels:
                        if channel.name == "notifs-partiels":
                            ping = await self.config.guild(guild).pinggroup()
                            if ping == None:
                                ping = "@everyone"
                            else:
                                ping = "<@&" + str(ping) + ">"
                            await channel.send(yeet + ping)
    #async def broadcast(self, message):
    #    """Envoie un message sur tous les channels notifs-partiels"""
    #    for guild in self.bot.guilds:
    #        for channel in guild.channels:
    #            if channel.name == 'notifs-partiels':
    #                await channel.send(message)

    @ commands.command()
    @ checks.is_owner()
    async def setinsausername(self, ctx, username):
        """Met à jour le nom de l'utilisateur du CAS Insa utilisé pour le scrapping"""
        await self.config.username.set(username)
        self.username = username
        await ctx.send("Nom d'utilisateur INSA mis à jour")

    @ commands.command()
    @ checks.is_owner()
    async def setinsapassword(self, ctx, password):
        """Met à jour le mot de passe de l'utilisateur du CAS Insa utilisé pour le scrapping"""
        await self.config.password.set(password)
        self.password = password
        await ctx.send("Mot de passe INSA mis à jour")

    @ commands.command()
    @ checks.is_owner()
    async def setscrapefrequency(self, ctx, frequency):
        """Définit à quelle fréquence (en s) le scrapping doit s'effectuer
            La nouvelle fréquence est appliquée au prochain scrapping.
        """
        try:
            self.frequency = int(frequency)
        except ValueError:
            await ctx.send("La fréquence doit être un entier")
            return

        await self.config.frequency.set(self.frequency)
        await ctx.send("Fréquence mise à jour")

    @ commands.command()
    @ checks.is_owner()
    async def setpinggroup(self, ctx, group):
        """Définit le group qui doit être ping pour une nouvelle note."""
        # The context's guild is defined
        if ctx.guild == None:
            await ctx.send("Faut m'envoyer ça sur un serveur…")
            return
        # Assertions on the group that's given
        # It does begin with @
        if not re.compile(r"<@&(\d+)>").match(group):
            if group == "@everyone":
                # Special case, remove any current setting
                await self.config.guild(ctx.guild).pinggroup.clear()
                await ctx.send("Le 'ping group' a été re-réglé à @everyone. 👍")
            elif group == "@here":
                await ctx.send("Je vais pas ping 'here' c'est bizarre... 🤨")
            else:
                await ctx.send(f"On dirait pas un groupe : '{group}' 🤔")
            return
        # If the group is valid, extract its id
        # The string given in that case is always '<@&0000000000>'
        # (but without constant zeros)
        gid = int(group[3:-1])
        role = ctx.guild.get_role(gid)
        if not role:
            await ctx.send(f"Je ne trouve pas {group}={gid} sur ce serveur...")
            return
        # Stuff is saved in the guild-specific config
        await self.config.guild(ctx.guild).pinggroup.set(gid)
        await ctx.send(f"Le 'ping group' a été réglé à <@&{gid}>. 👍")

    @ commands.command()
    @ checks.admin_or_permissions(manage_guild=True)
    async def getscrapefrequency(self, ctx):
        """Récupère la fréquence de scrapping actuelle"""
        await ctx.send('La fréquence de recherche est de {} secondes'.format(self.frequency))
