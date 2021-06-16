import discord
from discord.ext import commands

# Deathroll Game
import deathroll as dr

deathroll_invites = {}  # This does not seem like a good idea
deathroll_games = {}


class DeathrollCommands(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(name='deathroll_invite')
    async def deathroll_invite(self, ctx, opponent: discord.User, bet: int):
        global deathroll_invites

        author = ctx.message.author
        if(self.deathroll_game_with(author) is not None):
            message = f'{author.mention}, how about you finish your game first!'
        elif(self.deathroll_inv_from(author, opponent) is not None):
            message = (f'{author.mention}, you already have a pending invitation '
                       f'towards {opponent.display_name}')
        else:
            if(self.db.get_gold(author.id) < bet):
                message = f'{author.mention}, you are too broke for that bet.'
            else:
                invite = dr.Invite(author, bet, ctx.message.channel)
                deathroll_invites.setdefault(
                    opponent.id, []).append(invite)
                message = (f'<@{opponent.id}>, <@{author.id}> '
                           'has invited you to a deathroll game.\n'
                           f'Bet: {bet} gold')

        await ctx.send(message)

    @commands.command(name='deathroll_accept')
    async def deathroll_accept(self, ctx, opponent: discord.User):
        global deathroll_games, deathroll_invites

        author = ctx.message.author
        invite = self.deathroll_inv_from(opponent, author)

        if(self.deathroll_game_with(author) is not None):
            message = (f'{author.mention} finish your current game before '
                       'accepting another invite.')
        elif(invite is None):
            message = (f'{author.mention}, there is no pending invitation from '
                       f'{opponent.display_name}.  To see all of your pending'
                       'invitations, you can use `$invites`')
        elif(invite.channel is not ctx.message.channel):
            message = (f'{author.mention}, invitations need to be accepted '
                       f'in the same channels that they were sent in.  '
                       f'You need to accept this invitation in #{invite.channel}')
        elif(invite.is_expired()):
            self.delete_inv_to(author, invite)
            message = (f'{author.mention}, the invitation from '
                       f'{opponent.display_name} has expired, and has now '
                       f'been deleted.  Ask them to send another invitation.')
        elif(self.db.get_gold(author.id) < invite.bet):
            message = f'{author.mention}, you can\'t afford to bet that much.'
        elif(self.db.get_gold(opponent.id) < invite.bet):
            message = f'{opponent.mention}, can\'t afford to bet that much anymore.'
        else:
            game = dr.Game(opponent, author, invite.bet)
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
        global deathroll_invites

        author = ctx.message.author
        invite = self.deathroll_inv_from(opponent, author)
        if(invite is None):
            message = (f'{author.mention}, you have no invitations '
                       f'from the user {opponent.display_name}')
        else:
            deathroll_invites[author.id].remove(invite)
            if(len(deathroll_invites[author.id]) == 0):
                del deathroll_invites[author.id]
            message = (f'{opponent.mention}, {author.mention} '
                       'has declined your invitation.')

        await ctx.send(message)

    @commands.command(name='deathroll')
    async def deathroll(self, ctx):
        author = ctx.message.author
        game = self.deathroll_game_with(author)
        if(game is None):
            message = f'{author.mention} you are not in a game right now.'
        elif(game.turn.id is not author.id):
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
        max_afk_time = 180.0  # seconds
        author = ctx.message.author
        game = self.deathroll_game_with(author)
        if(game is None):
            message = f'{author.mention} you are not in a game right now.'
        elif(game.get_opponent(author) is not opponent):
            message = (f'{author.mention} you are not in a game with '
                       f'{opponent.display_name} right now.')
        elif(game.t_since_roll(opponent) > max_afk_time):
            message = (f'{opponent.mention} has not been active in over three '
                       'minutes, they have automically surrendered the game')
            self.deathroll_win(winner=author, loser=opponent, game=game)
        else:
            time_left = max_afk_time - game.t_since_roll(opponent)
            message = (f'{author.mention}, your opponent is not AFK yet.\n'
                       f'They still have {time_left} seconds.')

        await ctx.send(message)

    def deathroll_win(self, winner: discord.User, loser: discord.User, game: dr.Game):
        global deathroll_games

        # Distributes gains and losses
        self.db.update_gold(winner, game.bet)
        self.db.update_gold(loser, -game.bet)

        # Game is over, we delete them from the set of games
        del deathroll_games[winner.id]
        del deathroll_games[loser.id]

        message = (f'{winner.mention} has won {game.bet} gold!')
        return message

    # Returns the game that the user with id is in, or None

    def deathroll_game_with(self, player: discord.User):
        global deathroll_games

        try:
            game = deathroll_games[player.id]
        except(KeyError):
            game = None  # don't think it's necessary to throw an error here
        return game

    # Returns an invitation from p1_id towards p2_id

    def deathroll_inv_from(self, p1: discord.User, p2: discord.User):
        global deathroll_invites

        try:
            for invite in deathroll_invites[p2.id]:
                if(invite.player.id is p1.id):
                    return invite
        except(KeyError):
            return None  # don't think it's necessary to throw an error here
        return None

    def delete_inv_to(self, player: discord.User, invite: dr.Invite):
        global deathroll_invites

        deathroll_invites[player.id].remove(invite)
        if(len(deathroll_invites[player.id]) == 0):
            del deathroll_invites[player.id]


