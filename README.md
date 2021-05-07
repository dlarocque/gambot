# Gambot
Discord bot that tracks members' interactions in a server and awards them points accordingly.
The points that members earn through their interactions with others can then be used to wager in games of chance against other members in the server.

In the future, players will be able to spend their points on items and roles!

# Contributing
**I have no idea what I'm doing with Python and databases, please help my code not suck** 

## Commands

`!help` lists all commands along with their descriptions

`!points` sends a message telling the user how many points they currently have as well as their lifetime earnings.

`!deathroll <points> <second player>` sends an offer to the second player to start a deathroll game.  The second player can then accept the offer to play a game by sending `!acceptdr <first player> <points>`.  The first player must then `!roll <points>` with the inital bet.  The second player will then `!roll <points>` the amount that the first player rolled.  This sequence until a player rolls a 1 and loses.  Winner takes all.
