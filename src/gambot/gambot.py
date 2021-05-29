# gambot.py
# IMPORTS

import os

# Discord imports
import discord
from discord.ext import commands

from dotenv import load_dotenv

# Database imports
import psycopg2

import deathroll as dr

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
connection = None  # Connection to database
cursor = None     # Cursor in connection

deathroll_games = {}  # Deathroll games in progress
deathroll_invites = {}  # Pending deathroll invitations

# Connect to PostgreSQL database


def connect():
    global cursor
    global connection

    try:
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(
            user='postgres',
            password=PSQL_PASS,
            host='localhost',
            port='5432',
            database='postgres'
        )

        cursor = connection.cursor()
    except(Exception, psycopg2.Error) as error:
        print(error)
    finally:
        if connection is not None:
            print('Successfully connected to PostgreSQL database.\n')
            print('PostgreSQL version: ')
            cursor.execute('SELECT version()')
            print(cursor.fetchone())
            print()  # :)


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

    connection.commit()  # Commit changes to database
    print('Done collecting user data.\n')


# Called when a message is sent in a guild the bot is connected to
@bot.event
async def on_message(message):
    global connection
    global cursor

    # Do not respond to bots
    if message.author.bot:
        return

    update_gold(message.author, 1)

    # Unique message response
    if message.content == 'Hey Gambot':
        await message.channel.send(f'Hey {message.author.display_name}, https://www.youtube.com/watch?v=KLuX1oj1wHc.')

    # The on_message method looks at every single message, and can prevent
    # bot commands from being read in, so we do this to prevent that.
    await bot.process_commands(message)


@bot.command(name='deathroll_invite')
async def deathroll_invite(ctx, opponent: discord.User, bet: int):
    global deathroll_invites

    author = ctx.message.author
    if(deathroll_game_with(author) is not None):
        message = f'{author.mention}, how about you finish your game first!'
    elif(deathroll_inv_from(author, opponent) is not None):
        message = (f'{author.mention}, you already have a pending invitation '
                   f'towards {opponent.display_name}')
    else:
        if(get_gold(author.id) < bet):
            message = f'{author.mention}, you are too broke for that bet.'
        else:
            invite = dr.Invite(author, bet)
            deathroll_invites.setdefault(opponent.id, []).append(invite)
            message = (f'<@{opponent.id}>, <@{author.id}> '
                       'has invited you to a deathroll game.\n'
                       f'Bet: {bet} gold')

    await ctx.send(message)


@bot.command(name='deathroll_accept')
async def deathroll_accept(ctx, opponent: discord.User):
    global deathroll_games
    global deathroll_invites

    author = ctx.message.author
    invite = deathroll_inv_from(opponent, author)
    # I should probably refactor this somehow
    if(deathroll_game_with(author) is not None):
        message = (f'{author.mention} finish your current game before '
                   'accepting another invite.')
    elif(invite is None):
        message = (f'{author.mention}, there is no pending invitation from '
                   f'{opponent.display_name}.  To see all of your pending'
                   'invitations, you can use `$invites`')
    elif(get_gold(author.id) < invite.bet):
        message = f'{author.mention}, you can\'t afford to bet that much.'
    elif(get_gold(opponent.id) < invite.bet):
        message = f'{opponent.mention}, can\'t afford to bet that much anymore.'
    else:
        game = dr.Game(opponent, author, invite.bet)
        deathroll_games[opponent.id] = game
        deathroll_games[author.id] = game
        deathroll_invites[author.id].remove(invite)

        if(len(deathroll_invites[author.id]) == 0):  # odd, but works i guess
            del deathroll_invites[author.id]

        message = ('Deathroll game has begun!\n'
                   'Players:\n'
                   f'<@{opponent.id}>\nVS\n'
                   f'<@{author.id}>\n\n'
                   f'Bet: {invite.bet}\n\n'
                   f'<@{opponent.id}> must roll first with `$deathroll`')

    await ctx.send(message)


@bot.command(name='deathroll_decline')
async def deathroll_decline(ctx, opponent: discord.User):
    global deathroll_invites

    author = ctx.message.author
    invite = deathroll_inv_from(opponent, author)
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


@bot.command(name='deathroll')
async def deathroll(ctx):
    global deathroll_games

    author = ctx.message.author
    game = deathroll_game_with(author)
    if(game is None):
        message = f'{author.mention} you are not in a game right now.'
    elif(game.turn.id is not author.id):
        message = f'{author.mention}, it is not your turn.'
    else:
        roll = game.roll(author)

        if(roll == 0):
            message = deathroll_win(game.get_opponent(author), author, game)
        else:
            message = (f'{author.mention} rolled a {roll}\n'
                       'The game continues.\n'
                       f'Next roll: 0 - {roll}')

    await ctx.send(message)


@bot.command(name='deathroll_abandoned')
async def deathroll_abandoned(ctx, opponent: discord.User):
    global deathroll_games

    max_afk_time = 180.0  # seconds
    author = ctx.message.author
    game = deathroll_game_with(author)
    if(game is None):
        message = f'{author.mention} you are not in a game right now.'
    elif(game.get_opponent(author) is not opponent):
        message = (f'{author.mention} you are not in a game with '
                   f'{opponent.display_name} right now.')
    elif(game.t_since_roll(opponent) > max_afk_time):
        message = (f'{opponent.mention} has not been active in over three '
                   'minutes, they have automically surrendered the game')
        deathroll_win(winner=author, loser=opponent, game=game)
    else:
        time_left = max_afk_time - game.t_since_roll(opponent)
        message = (f'{author.mention}, your opponent is not AFK yet.\n'
                   f'They still have {time_left} seconds.')

    await ctx.send(message)


def deathroll_win(winner: discord.User, loser: discord.User, game: dr.Game):
    global deathroll_games

    # Distributes gains and losses
    update_gold(winner, game.bet)
    update_gold(loser, -game.bet)

    # Game is over, we delete them from the set of games
    del deathroll_games[winner.id]
    del deathroll_games[loser.id]

    message = (f'{winner.mention} has won {game.bet} gold!')
    return message


# Returns the game that the user with id is in, or None
def deathroll_game_with(player: discord.User):
    global deathroll_games

    try:
        game = deathroll_games[player.id]
    except(KeyError):
        game = None  # don't think it's necessary to throw an error here
    return game


# Returns an invitation from p1_id towards p2_id
def deathroll_inv_from(p1: discord.User, p2: discord.User):
    global deathroll_invites

    try:
        for invite in deathroll_invites[p2.id]:
            if(invite.player.id is p1.id):
                return invite
    except(KeyError):
        return None  # don't think it's necessary to throw an error here
    return None


@bot.command(name='gold')
async def gold(ctx):
    """Tells the user how much gold they have
    """
    global cursor

    cursor.execute('''
                    SELECT gold from gambot.gold
                    WHERE user_id = %s
                    ''', (ctx.message.author.id, ))
    gold = cursor.fetchone()[0]
    await ctx.send(f'{ctx.message.author.display_name} has {gold} gold.')


@bot.command(name='invites')
async def invites(ctx):
    global deathroll_invites

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


@bot.command(name='github', help='Sends a link to Gambot\'s GitHub repo.')
async def github(ctx):
    await ctx.send('https://github.com/dlarocque/Gambot')


def update_gold(user: discord.User, to_add: int):
    global cursor
    global connection

    print(f'updated {user.display_name} gold by {to_add}')

    cursor.execute('''
                    UPDATE gambot.gold
                    SET gold = gold + %s
                    WHERE user_id = %s
                   ''', (to_add, user.id))
    connection.commit()  # Commit changes to gambot.gold


def get_gold(user_id):
    global cursor

    cursor.execute('''
                    SELECT gold FROM gambot.gold
                    WHERE user_id = %s
                    ''', (user_id, ))
    output = cursor.fetchone()  # returns a tuple if the user exists
    if(output is not None):
        gold = output[0]
        return gold
    return None


# This might be unecessary, but whatever
if __name__ == '__main__':
    connect()
    print('Connecting Gambot to Discord...')
    bot.run(TOKEN)