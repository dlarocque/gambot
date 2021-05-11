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
bot = commands.Bot(command_prefix='$', intents=intents)

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
            # If the user does not exist in the gambot.users table
            if(cursor.fetchone() is None):
                print(f'Collecting data for new user: {member.display_name}')
                cursor.execute('''
                                INSERT INTO gambot.users
                                (user_id, discriminator, guild_name,
                                display_name)
                                VALUES (%s, %s, %s, %s)
                               ''',
                               (member.id, member.discriminator, guild.name,
                                member.display_name))
                cursor.execute('''
                               INSERT INTO gambot.gold
                               (user_id, gold)
                               VALUES (%s, %s)
                               ''',
                               (member.id, 0))

    connection.commit() # Commit changes to database
    print('Done collecting user data.\n')


# Called when a message is sent in a guild the bot is connected to
@bot.event
async def on_message(message):
    global connection
    global cursor

    # Do not respond to bots
    if message.author.bot:
        return

    update_gold(message.author.id, 1)

    # Unique message response
    if message.content == 'Hey Gambot':
        await message.channel.send(f'Hey {message.author.display_name} :)')

    # The on_message method looks at every single message, and can prevent
    # bot commands from being read in, so we do this to prevent that.
    await bot.process_commands(message)


@bot.command(name='deathroll')
async def deathroll(ctx):
    """Start a deathroll game between two players

    Starts a deathroll game between two players if the conditions
    for starting a deathroll game are met.
    ** See README.md for more information on the rules of the game **

    Conditions for a deathroll game:
    1. Players must not be in an existing deathroll game.
    2. Both players must have enough gold to satisfy the wager.

    Keyword arguments:
    ctx: context that the command was written in
    """
    output = 'Starting a deathroll match.\n'

    await ctx.send(output)


@bot.command(name='roll')
async def roll(ctx):
    """Rolls for a player once it is their turn

    Once a deathroll game is started between two players, both players
    have to alternate turns by executing this command to play their turn.
    The roll is from 0 to game.prev_roll.

    Conditions for a roll:
    1. The member exeucting the command must be in a deathroll game.
    2. The roll command must be executed from the same channel that
    the deathroll game was started in.

    Keyword arguments:
    ctx: context that the command was written in
    """
    output = 'temp'


    await ctx.send(output)


@bot.command(name='github', help='Sends a link to Gambot\'s GitHub repo.')
async def github(ctx):
    await ctx.send('https://github.com/dlarocque/Gambot')


def update_gold(user_id, to_add):
    global cursor
    global connection

    cursor.execute('''
                   UPDATE gambot.gold
                   SET gold = gold + %s
                   WHERE user_id = %s
                   ''', (to_add, user_id))
    connection.commit() # Commit changes to gambot.gold


# This might be unecessary, but whatever
if __name__ == '__main__':
    connect()
    print('Connecting Gambot to Discord...')
    bot.run(TOKEN)
