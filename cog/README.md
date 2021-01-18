# Cog Insanoetdur

Ceci est un cog Red Discord Bot qui replique les fonctionnalités de la version NodeJS d'Insanotedur.

Les identifiants de connexion sont stockés en utlisant la classe `Config` de Red Discord Bot. Fais attention à qui peut accéder au fichier correspondant créé sur le disque car il pourra voir les identifiants en clair ! 

## Commandes

### Discord

`[p]` désigne le préfixe utilisé par Discord Red Bot.

`[p]setscrapefrequency`: Fixe la fréquence de scrapping du bot, en secondes.
`[p]getscrapefrequency`: Renvoie la fréquence de scrapping du bot. Admin seulement.
`[p]setinsausername`: Fixe le nom d'utilisateur utilisé pour le scrapping. Owner seulement.
`[p]setinsapassword`: Fixe le mot de passe utlisé pour le scrapping. A ne pas faire n'importe où ! Owner seulement.

### CLI

Pour avoir plus d'informations de debug, lancer le bot avec `redbot [nombot] --debug`