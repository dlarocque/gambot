# gambot.py
import os

# Discord imports
import discord
from dotenv import load_dotenv
from discord.ext import commands

# Database imports
import psycopg2

# Load from environment
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PSQL_PASS = os.getenv('PSQL_PASS')

# Set command Prefix
bot = commands.Bot(command_prefix=';')

# Connect to PostgreSQL database
def connect():
    try:
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect (
        user = 'postgres',
        password = PSQL_PASS,
        host = 'localhost',
        port = '5432',
        database = 'postgres'
        )

        cur = connection.cursor()

        print('PostgreSQL version: ')
        cur.execute('SELECT version()')
        print(cur.fetchone())

        # When should we close the connection to the database?

    except(Exception, psycopg2.error) as error:
        print(error)
    finally:
        if connection is not None:
            print('Successfully connected to PostgreSQL database.\n')



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


# This might be unecessary, but whatever
if __name__ == '__main__':
    connect()
    print('Connecting Gambot to Discord...')
    bot.run(TOKEN)