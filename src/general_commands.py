# Discord imports
import discord
from discord.ext import commands

from database import cursor
from deathroll_commands import deathroll_invites


class GeneralCommands(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.Cog.listener()
    async def on_message(self, message):
        # Do not respond to bots
        if message.author.bot:
            return

        # Move this to a database import not gambot
        self.db.update_gold(message.author, 1)

        # Unique message response
        if message.content == 'Hey Gambot':
            await message.channel.send(f'Hey {message.author.display_name}, https://www.youtube.com/watch?v=KLuX1oj1wHc.')

        # The on_message method looks at every single message, and can prevent
        # bot commands from being read in, so we do this to prevent that.
        # await bot.process_commands(message)

    @commands.command(name='gold')
    async def gold(self, ctx):
        """Tells the user how much gold they have
        """
        gold = self.db.get_gold(ctx.message.author.id)
        await ctx.send(f'{ctx.message.author.display_name} has {gold} gold.')

    @commands.command(name='invites')
    async def invites(self, ctx):
        try:
            invites = deathroll_invites[ctx.message.author.id]
            if(invites is None):
                raise KeyError  # should fix this

            message = f'{ctx.message.author.mention}\'s invitations:\n'
            for invite in invites:
                message += str(invite) + '\n'
        except(KeyError):
            message = f'{ctx.message.author.mention} has no pending invitations'

        await ctx.send(message)

    @commands.command(name='github', help='Sends a link to Gambot\'s GitHub repo.')
    async def github(self, ctx):
        await ctx.send('https://github.com/dlarocque/Gambot')
