# Discord import
import discord
from discord.ext import commands

from database import cursor
from deathroll_commands import deathroll_invites


class GeneralCommands(commands.Cog):
    """General commands for the Discord bot"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.Cog.listener()
    async def on_message(self, message):
        # Do not respond to bots
        if message.author.bot:
            return

        self.db.update_gold(message.author, 1)

        if message.content == 'Hey Gambot':
            await message.channel.send(f'Hey {message.author.display_name}, https://www.youtube.com/watch?v=KLuX1oj1wHc.')

    @commands.command(name='gold')
    async def gold(self, ctx):
        """Tells the user how much gold they have"""
        gold = self.db.get_gold(ctx.message.author.id)
        await ctx.send(f'{ctx.message.author.display_name} has {gold} gold.')

    @commands.command(name='invites')
    async def invites(self, ctx):
        """Sends a message containing all of the authors pending invitations"""
        try:
            invites = deathroll_invites[ctx.message.author.id]
            if(invites is None):
                raise KeyError  # FIX TODO

            message = f'{ctx.message.author.mention}\'s invitations:\n'
            for invite in invites:
                message += str(invite) + '\n'
        except(KeyError):  # FIX TODO
            message = f'{ctx.message.author.mention}, you have no pending invitations'

        await ctx.send(message)

    @commands.command(name='github')
    async def github(self, ctx):
        """Sends a link to the GitHub repo containing Gambots source code"""
        await ctx.send('https://github.com/dlarocque/Gambot')

    @commands.command(name='commands')
    async def commands(self, ctx):
        """Provides a user some basic information on how to use Gambot"""
        await ctx.send('For a full list of commands, visit here: https://github.com/dlarocque/gambot/docs/COMMANDS.md')
