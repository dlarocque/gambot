import discord
from discord.ext import commands

# Database imports
import psycopg2

cursor = None
connection = None


class Database(commands.Cog):
    def __init__(self, bot, password):
        self.bot = bot
        self.password = password

    def connect(self):
        global cursor
        global connection

        try:
            print('Connecting to the PostgreSQL database...')
            connection = psycopg2.connect(
                user='postgres',
                password=self.password,
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

    # Collect the data from all of the users

    def collect_data(self):
        global cursor
        global connection

        print('\nCollecting user data in guilds...')

        for guild in self.bot.guilds:
            for member in guild.members:
                cursor.execute('''
                            SELECT user_id FROM gambot.users
                            WHERE user_id = %s;
                            ''', [member.id])
                # If the user does not exist in the gambot.users table
                if(cursor.fetchone() is None):
                    print(
                        f'Collecting data for new user: {member.display_name}')
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

    def update_gold(self, user: discord.User, to_add: int):
        global cursor
        global connection

        print(f'updated {user.display_name} gold by {to_add}')

        cursor.execute('''
                        UPDATE gambot.gold
                        SET gold = gold + %s
                        WHERE user_id = %s
                    ''', (to_add, user.id))
        connection.commit()  # Commit changes to gambot.gold

    def get_gold(self, user_id):
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
