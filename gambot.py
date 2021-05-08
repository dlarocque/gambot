# gambot.py
import os

# Discord imports
import discord
from dotenv import load_dotenv
from discord.ext import commands

# Database imports
import psycopg2

# Connect to database

PSQL_PASS = os.getenv('PSQL_PASS')
try:
    connection = psycopg2.connect (
        user = 'postgres',
        password = PSQL_PASS,
        host = 'localhost',
        port = '5432',
        database = 'postgres'
    )
except(Exception, psycopg2.error) as error:
        print("Error connecting to database")


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix=';')


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
    await ctx.send('https://github.com/dlarocque/Gambot')


bot.run(TOKEN)