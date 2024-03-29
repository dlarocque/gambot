import discord
from discord.ext import commands
import deathroll as dr

deathroll_invites = {}
deathroll_games = {}


class DeathrollCommands(commands.Cog):
    """All of the commands necessary for a deathroll game"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(name='deathroll_invite')
    async def deathroll_invite(self, ctx, opponent: discord.User, bet: int):
        """Sends an invitation to a deathroll game to another player

        Keyword Arguments:
            ctx: context that the command was sent in
            opponent (discord.User): the user that the invitation is sent to
            bet (int): the amount of gold that is to be bet
        """
        global deathroll_invites

        author = ctx.message.author
        if self.deathroll_game_with(author):
            message = f'{author.mention}, how about you finish your game first!'
        elif self.deathroll_inv_from(author, opponent):
            message = (
                f'{author.mention}, you already have a pending invitation '
                f'towards {opponent.display_name}')
        else:
            if self.db.get_gold(author.id) < bet:
                message = f'{author.mention}, you are don\'t have enough gold for that bet.'
            else:
                invite = dr.DeathrollInvite(author, bet, ctx.message.channel)
                deathroll_invites.setdefault(
                    opponent.id, []).append(invite)
                message = (f'<@{opponent.id}>, <@{author.id}> '
                           'has invited you to a deathroll game.\n'
                           f'Bet: {bet} gold')

        await ctx.send(message)

    @commands.command(name='deathroll_accept')
    async def deathroll_accept(self, ctx, opponent: discord.User):
        """Accepts an incoming invitation to a deathroll game

        Keyword Arguments:
            ctx: context that the command was sent in
            opponent (discord.User): the player who sent the invitations
        """
        global deathroll_games, deathroll_invites

        author = ctx.message.author
        invite = self.deathroll_inv_from(opponent, author)

        if self.deathroll_game_with(author):
            message = (f'{author.mention} finish your current game before '
                       'accepting another invite.')
        elif invite is None:
            message = (
                f'{author.mention}, there is no pending invitation from '
                f'{opponent.display_name}.  To see all of your pending'
                'invitations, you can use `$invites`')
        elif invite.channel is not ctx.message.channel:
            message = (
                f'{author.mention}, invitations need to be accepted '
                f'in the same channels that they were sent in.  '
                f'You need to accept this invitation in #{invite.channel}')
        elif invite.is_expired():
            self.delete_inv_to(author, invite)
            message = (f'{author.mention}, the invitation from '
                       f'{opponent.display_name} has expired, and has now '
                       f'been deleted.  Ask them to send another invitation.')
        elif self.db.get_gold(author.id) < invite.bet:
            message = f'{author.mention}, you can\'t afford to bet that much.'
        elif self.db.get_gold(opponent.id) < invite.bet:
            message = f'{opponent.mention}, can\'t afford to bet that much anymore.'
        else:
            game = dr.DeathrollGame(
                opponent, author, invite.bet, invite.channel)
            # We add the instance of the game in the dictionary, where the keys are the players' id's
            # It exists in both positions so that we are able to determine if each player is in a game.
            deathroll_games[opponent.id] = game
            deathroll_games[author.id] = game
            self.delete_inv_to(author, invite)

            message = ('Deathroll game has begun!\n'
                       'Players:\n'
                       f'<@{opponent.id}>\nVS\n'
                       f'<@{author.id}>\n\n'
                       f'Bet: {invite.bet}\n\n'
                       f'<@{opponent.id}> must roll first with `$deathroll`')

        await ctx.send(message)

    @commands.command(name='deathroll_decline')
    async def deathroll_decline(self, ctx, opponent: discord.User):
        """Declines a deathroll invitation from another user

        Keyword Arguments:
            ctx: context that the command was sent in
            opponent (discord.User): the user who's invitation is declined
        """
        global deathroll_invites

        author = ctx.message.author
        invite = self.deathroll_inv_from(opponent, author)

        if invite is None:
            message = (f'{author.mention}, you have no invitations '
                       f'from the user {opponent.display_name}')
        else:
            deathroll_invites[author.id].remove(invite)
            # this is done to make it easier to check if there are no invites
            if len(deathroll_invites[author.id]) == 0:
                del deathroll_invites[author.id]

            message = (f'{opponent.mention}, {author.mention} '
                       'has declined your invitation.')

        await ctx.send(message)

    @commands.command(name='deathroll')
    async def deathroll(self, ctx):
        """Plays a players' turn in a deathroll game

        Keyword Arguments:
            ctx: context that the command was sent in
        """
        author = ctx.message.author
        game = self.deathroll_game_with(author)

        if game is None:
            message = f'{author.mention} you are not in a game right now.'
        elif game.channel is not ctx.message.channel:
            message = (f'{author.mention}, games must be played in the same '
                       f'channels that they started in.  Try again in the '
                       f'#{game.channel} channel.')
        elif game.turn.id is not author.id:
            message = f'{author.mention}, it is not your turn.'
        else:
            roll = game.roll()

            if(roll == 0):
                message = self.deathroll_win(
                    game.get_opponent(author), author, game)
            else:
                message = (f'{author.mention} rolled a {roll}\n'
                           'The game continues.\n'
                           f'Next roll: 0 - {roll}')

        await ctx.send(message)

    @commands.command(name='deathroll_abandoned')
    async def deathroll_abandoned(self, ctx, opponent: discord.User):
        """Checks to see if the opponent has abandoned a deathroll game

        When a player does not play their turn in a deathroll game, their opponent
        can choose to accuse them of abandoning the game.  If the accused player
        has not rolled in 'max_afk_time' seconds, then the accuser wins.

        Keyword Arguments:
            ctx: context that the command was sent in
            opponent (discord.User): the other player in the deathroll game
        """
        max_afk_time = 180.0  # seconds
        author = ctx.message.author
        game = self.deathroll_game_with(author)

        if game is None:
            message = f'{author.mention} you are not in a game right now.'
        elif game.get_opponent(author) is not opponent:
            message = (f'{author.mention} you are not in a game with '
                       f'{opponent.display_name} right now.')
        elif game.t_since_roll(opponent) > max_afk_time:
            message = (f'{opponent.mention} has not been active in over three '
                       'minutes, they have automically surrendered the game')
            self.deathroll_win(winner=author, loser=opponent, game=game)
        else:
            time_left = max_afk_time - game.t_since_roll(opponent)
            message = (f'{author.mention}, your opponent is not AFK yet.\n'
                       f'They still have {time_left} seconds.')

        await ctx.send(message)

    def deathroll_win(
            self,
            winner: discord.User,
            loser: discord.User,
            game: dr.DeathrollGame):
        """Handles a deathroll game when a player wins

        Distributes the winnings, deletes the deathroll game

        Keyword Arguments:
            winnner (discord.User): the winner of the deathroll game
            loser (discord.User): the loser of the deathroll game
            game (dr.DeathrollGame): the deathroll game that was won
        """
        global deathroll_games

        self.db.update_gold(winner, game.bet)
        self.db.update_gold(loser, -game.bet)

        del deathroll_games[winner.id]
        del deathroll_games[loser.id]

        message = (f'{winner.mention} has won {game.bet} gold!')
        return message

    def deathroll_game_with(self, player: discord.User):
        """Returns the game that a player is in
        
        Keyword Arguments:
            player (discord.User): the player who's game is to be returned

        Returns:
            game (deathroll.DeathrollGame): the game that player is in
            None: the player is not in a game
        """
        global deathroll_games

        try:
            game = deathroll_games[player.id]
        except(KeyError): # FIX TODO
            game = None  # don't think it's necessary to throw an error here
        return game

    # Returns an invitation from p1_id towards p2_id

    def deathroll_inv_from(self, player1: discord.User, player2: discord.User):
        """Returns an invitation from player1 towards player2
        
        Returns:
            invite (deathroll.DeathrollInvite): the invite to player2 from player1
            None: there is no existing invite to player2 from player1
        """
        global deathroll_invites

        try:
            for invite in deathroll_invites[player2.id]:
                if invite.player.id is player1.id:
                    return invite
        except(KeyError):
            return None  # don't think it's necessary to throw an error here
        return None

    def delete_inv_to(self, player: discord.User, invite: dr.DeathrollInvite):
        """Deletes an invitation towards a player
        
        Keyword Arguments: 
            invite (deathroll.Invite): invitation to be deleted
            player (discord.User): the user who the invite is sent to
        """
        global deathroll_invites

        deathroll_invites[player.id].remove(invite)
        if len(deathroll_invites[player.id]) == 0:
            del deathroll_invites[player.id]
