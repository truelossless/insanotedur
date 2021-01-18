# Insanotedur standalone

Version originelle du bot en Node.js, fonctionnant avec Discord.js.

## Créer son propre bot

Si tu veux modifier/faire ton propre bot Insanotedur:

Crée un fichier config.json à la racine du dossier Insanotedur.  
Ces paramètres doivent être remplis:  
    - username: le nom utilisé pour se connecter à l'ENT Insa  
    - password: le mdp utilisé  
    - frequency: la fréquence de rafraichissement en secondes (pas trop fréquent sinon tu risques de te faire ban !)  
    - token: le token d'authentification de ton bot discord.

Le bot postera automatiquement un message dans tous les serveurs où il est, dans le channel #notifs-partiels.

Le projet est sous licence MIT donc fais en ce que tu veux :)

## Commandes

### Discord

`yo`: le bot répond avec broooo. Permet de savoir si le bot fonctionne bien.

### CLI

`idle`: active/désactive le mode idle (n'envoie pas de requête mais réagit aux msgs Discord)  
`debug`: active/désactive les messages de debug.  
`msg [message]`: envoie à tous les serveurs le message `[message]`.
