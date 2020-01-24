# Insanotedur

Reçois une notif Discord quand une nouvelle note de partiel 2A tombe !

## Rejoindre le serveur

Le plus simple pour profiter de mon bot est de rejoindre ce serveur !
Sois sur d'activer les notifs discord dans le salon #notifs-partiels

https://discord.gg/RRSTCx

## Inviter le bot sur son serveur

Tu peux aussi inviter le bot sur ton serveur Discord. Voici le lien:
https://discordapp.com/oauth2/authorize?client_id=647771450983579669&scope=bot&permissions=131072

## Créer son propre bot

Si tu veux modifier/faire ton propre bot Insanotedur:

Crée un fichier config.json à la racine du dossier Insanotedur.
Ces paramètres doivent être remplis:
    - username: le nom utilisé pour se connecter à l'ENT Insa
    - password: le mdp utilisé
    - frequency: la fréquence de rafraichissement (pas trop fréquent sinon tu risques de te faire ban !)
    - token: le token d'authentification de ton bot discord.

Le bot postera automatiquement un message dans tous les serveurs où il est, dans le channel #notifs-partiels.

Le projet est sous licence MIT donc fais en ce que tu veux :)

## Commandes

### Discord

yo: le bot répond avec broooo. Permet de savoir si le bot fonctionne bien.

### CLI

idle: active/désactive le mode idle (n'envoie pas de requête mais réagit aux msgs Discord)
debug: active/désactive les messages de debug.
msg [message]: envoie à tous les serveurs le message [message].
