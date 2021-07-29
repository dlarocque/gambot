import discord
from discord.ext import commands

# Database imports
import psycopg2

cursor = None
connection = None


class Database(commands.Cog):
    """PostgreSQL database for Gambot (local)"""

    def __init__(self, bot, password):
        self.bot = bot
        self.password = password

    def connect(self):
        """Connects to the PostgreSQL database using psycopg2

        Changes might need to be made if you're connecting this 
        to your own database.
        """
        global cursor
        global connection

        try:
            print('Connecting to the PostgreSQL database...')
            connection = psycopg2.connect(
                user='postgres',
                password=self.password,
                host='localhost',
                port='5432',
                database='gambot'
            )

            cursor = connection.cursor()
        except(Exception, psycopg2.Error) as error:
            print(error)
        finally:
            if connection:
                print('Successfully connected to PostgreSQL database.\n')
                print('PostgreSQL version: ')
                cursor.execute('SELECT version()')
                print(cursor.fetchone())
                print()  # :)

    def collect_data(self):
        """Collects all user data from all users in all servers if that data does not already exist"""
        global cursor
        global connection

        print('\nCollecting user data in guilds...')

        for guild in self.bot.guilds:
            for member in guild.members:
                cursor.execute('''
                            SELECT user_id FROM users
                            WHERE user_id = %s;
                            ''', [member.id])
                # If the user does not exist in the users table
                if cursor.fetchone() is None:
                    print(
                        f'Collecting data for new user: {member.display_name}')
                    cursor.execute('''
                                    INSERT INTO users
                                    (user_id, discriminator, guild_name,
                                    display_name)
                                    VALUES (%s, %s, %s, %s)
                                ''',
                                   (member.id, member.discriminator, guild.name,
                                    member.display_name))
                    cursor.execute('''
                                INSERT INTO gold
                                (user_id, gold)
                                VALUES (%s, %s)
                                ''',
                                   (member.id, 0))

        connection.commit()
        print('Done collecting user data.\n')

    def update_gold(self, user: discord.User, to_add: int):
        """Updated the amount of gold a user has

        The user should already exist in the database.  We don't check.
        
        Keyword Arguments:
            user (discord.User): The users to query
            to_add (int): amount of gold to add (negative to remove)
        """
        global cursor
        global connection

        print(f'updated {user.display_name} gold by {to_add}')

        cursor.execute('''
                        UPDATE gold
                        SET gold = gold + %s
                        WHERE user_id = %s
                    ''', (to_add, user.id))
        connection.commit()  # Commit changes to gold

    def get_gold(self, user_id):
        """Returns the amount of gold a user has
        
        Keyword Arguments:
            user_id: User id to be queried for gold

        Returns:
            gold: the amount of gold the user has
            None: the user does not exist
        """
        global cursor

        cursor.execute('''
                        SELECT gold FROM gold
                        WHERE user_id = %s
                        ''', (user_id, ))
        output = cursor.fetchone()  # returns a tuple if the user exists
        if output:
            gold = output[0]
            return gold
        return None
