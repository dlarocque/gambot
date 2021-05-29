# Gambot

[IN PROGESS]

Discord bot that tracks members' interactions in a server and awards them points accordingly.
The points that members earn through their interactions with others can then be gambled in a **deathroll** game!

In the future, I plan on adding a shop where users can spend their points on roles, as well as leaderboards where users can flex their virtual currencies to their friends. 

## Commands
#### General Commands

`$help` lists all commands along with their descriptions.

`$gold` Tells you how much gold you have.

`$invites` Lists all of the invitations that have been sent to you.

#### Deathroll Commands

For more information on deathrolling, scroll down to the **Deathroll rules** section.

`$deathroll_invite <@player> <bet>` Sends an invite for a deathroll game to `<@player>` if there is not already a pending invite, or you are not already in a deathroll game with someone else.  You need to have enough gold to satisfy the `<bet>` before making the invitation!

`$deathroll_accept <@player>` Accepts an invitation that was sent from `<@player>`, make sure you are willing to lose all of the gold that is in the bet!  As soon as you accept the invitation, you **must** keep playing until the game is done, or else you risk losing your bet.

`$deathroll_decline <@player>` Declines an invitation that was sent to you from `<@player>`.

`$deathroll` Plays a turn in the deathroll game that you are in if it is your turn.

`deathroll_abandoned <@player>` Accuse your opppoent, `<@player>` of abandoning the game.  If your opponent has not played his turn in over three minutes, then they will forfeit automatically, and you win the game.  Your opponent only forfeits if you accuse them of abandoning the game.

## Deathroll Rules

The rules to deathroll are simple. 
1. You and an opponent agree on how much gold you're willing to bet.  You can send an invite to an opponent with the `$deathroll_invite <@opponent> <bet>` command.  Your opponent can then accept your invite with `$deathroll_accept <@opponent>`.  The game begins.
2. The first player must start their turn with `$deathroll`, which will roll a number between 0 and `<bet>`.  The number that you roll will then be the range that your opponent can roll from. 
3. Your opponent plays their turn with `$deathroll`, which rolls a number from 0 to your last roll.  The range gets smaller and smaller every turn.
4. Continue the game until a player rolls a 0, or a player abandons the game.

**The first person to roll a 0 loses the game, and the opponent takes all.**

### Important Notes About Deathroll
1. Once you start a deathroll game with a user, you must be willing to play the game out until the end.  When it is your turn, you have 3 minutes until it is considered that you have abandoned the game.
2. The game must be played in the `#deathroll` channel within your server.  If this channel does not exist, Gambot will not let you play deathroll. This is just so that the games don't get confusing, and players know where to go to play games in larger servers. (I am currently trying to make it so that Gambot can read messages from any server with `#deathroll` in the channel name.)

## Want To Use This Bot?
If, for some reason you are interested in adding this bot to your server, see setup.txt for a quick guide on how to run this bot wherever you want.
This bot was made with the intention of being semi-private, so you're going to have to set it up to run on your own, I've tried making it easy to do so for my own sake though.

## Issues
If you encounter an issue as a user, or developer, **please** submit an issue on this GitHub page so that I can fix it right away.  Try to break the bot!

## Authors
- Me :)

## 
