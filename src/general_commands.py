# Discord imports
import discord
from discord.ext import commands

# Database imports
import database

# Deathroll Game
import deathroll as dr

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        # Do not respond to bots
        if message.author.bot:
            return

        # Move this to a database import not gambot
        # gambot.update_gold(message.author, 1) 

        # Unique message response
        if message.content == 'Hey Gambot':
            await message.channel.send(f'Hey {message.author.display_name}, https://www.youtube.com/watch?v=KLuX1oj1wHc.')

        # The on_message method looks at every single message, and can prevent
        # bot commands from being read in, so we do this to prevent that.
        # await bot.process_commands(message)
