# gambot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Gambot is connected to Discord.')
    print('Connected to the following guilds :')

    for guild in bot.guilds:
        print(guild.name)

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content == 'Hey Gambot':
        await message.channel.send(f'Hey {message.author.display_name} :)')

    # The on_message method looks at every single message, and can prevent
    # bot commands from being read in, so we do this to prevent that.
    await bot.process_commands(message)

@bot.command(name='github', help='Sends a link to Gambot\'s GitHub repo.')
async def github(ctx):
    print('user asked for github')
    await ctx.send('https://github.com/dlarocque/Gambot')

@bot.command(name='points')
async def points(ctx):
    # todo

@bot.command(name='deathroll')
async def deathroll(ctx, bet, opponent):
    await ctx.send(f'{ctx.author.display_name} has started a deathroll with @{opponent.display_name}')
    # todo

@bot.command(name='roll')
async def roll(ctx, bet):
    # todo
bot.run(TOKEN)
