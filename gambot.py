# gambot.py
import os

# Discord imports
import discord
from discord.ext import commands

from dotenv import load_dotenv

# Database imports
import psycopg2

# Load from environment
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PSQL_PASS = os.getenv('PSQL_PASS')

# Set command Prefix
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)

connection = None
cursor = None

# Connect to PostgreSQL database
def connect():
    global cursor
    global connection

    try:
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect (
        user = 'postgres',
        password = PSQL_PASS,
        host = 'localhost',
        port = '5432',
        database = 'postgres'
        )

        cursor = connection.cursor()
    except(Exception, psycopg2.error) as error:
        print(error)
    finally:
        if connection is not None:
            print('Successfully connected to PostgreSQL database.\n')
            print('PostgreSQL version: ')
            cursor.execute('SELECT version()')
            print(cursor.fetchone())
            print() # :)


@bot.event
async def on_ready():
    print('Gambot is connected to Discord.')
    print('Connected to the following guilds :')

    for guild in bot.guilds:
        print(guild.name)

    collect_data()

# Collect the data from all of the users
def collect_data():
    global cursor
    global connection

    print('\nCollecting user data in guilds...')

    for guild in bot.guilds:
        for member in guild.members:
            cursor.execute('''
                           SELECT user_id FROM gambot.users
                           WHERE user_id = %s;
                           ''', [member.id])
            output = cursor.fetchone()
            if(output is None):
                print(member.id)
#    connection.commit()
    print('Done collecting user data.\n')


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
