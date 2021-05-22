# gambot.py
# IMPORTS

import os

# Discord imports
import discord
from discord.ext import commands

from dotenv import load_dotenv

# Database imports
import psycopg2

import deathroll

# GLOBAL VARIABLES

# Environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PSQL_PASS = os.getenv('PSQL_PASS')

# Discord bot variables
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

# PostgreSQL database variables
connection = None # Connection to database
cursor = None     # Cursor in connection

deathroll_games = {} # Dictionary of deathroll games in progress,
# key = user_id, value = Deathroll_game

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


@bot.command(name='deathroll_start')
async def deathroll_start(ctx, opponent: discord.User, bet: int):
    """Start a deathroll game between two players

    Starts a deathroll game between two players if the conditions
    for starting a deathroll game are met.

    Conditions for a deathroll game:
    1. Players must not be in an existing deathroll game.
    2. Both players must have enough gold to satisfy the wager.

    Keyword arguments:
    ctx: context that the command was written in
    """
    global deathroll_games

    # Check to see if one of the users is already in a deathroll game
    if(deathroll_game_with(ctx.message.author.id) is not None):
        message = '{message.author.display_name} is already in a game.'
    elif(deathroll_game_with(opponent.id) is not None):
        message = '{opponent.display_name} is already in a game.'
    else:
        # Check to see if the users have enough gold to play a game
        if(get_gold(ctx.message.author.id) < bet):
            message = '{message.author.display_name} does not have nough gold.'
        elif(get_gold(opponent.id) < bet):
            message = '{opponent.id} does not have enough gold.'
        else:
            deathroll_games.push(deathroll.Game(ctx.msessage.author.id, opponent.id, bet))
            message = '''
                        Deathroll game has begun.\n
                        Players:\n
                        @%s\n
                        @%s\n
                        \n
                        Bet: %d\n
                        \n
                        @%s may now `$deathroll`.
                        '''
    await ctx.send(message)

@bot.command(name='deathroll')
async def deathroll(ctx):
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


@bot.command(name='deathroll_abandoned')
async def deathroll(ctx, oppenent):
    """Checks to see if an opponent has abandonded a game

    If the opponent has indeed abandoned the game, then the
    player who that player was oppposing automatically wins the
    deathroll game.
    """


def deathroll_win(winner, gold):
    """Rewards the winner of a deathroll game

    """


def deathroll_game_with(id):
    for deathroll_game in deathroll_games:
        if(deathroll_game.p1_id == id or deathroll_game.p2_id == id):
            return deathroll_game

    return None


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


def get_gold(user_id):
    global cursor

    cursor.execute('''
                    SELECT gold FROM gambot.gold
                    WHERE user_id = %s
                    ''', (user_id, ))
    output = cursor.fetchone() # returns a tuple if the user exists
    if(output is not None):
        gold = output[0]
        return gold
    return None
    


# This might be unecessary, but whatever
if __name__ == '__main__':
    connect()
    print('Connecting Gambot to Discord...')
    bot.run(TOKEN)
