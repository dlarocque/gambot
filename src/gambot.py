import os

# Discord imports
import discord
from discord.ext import commands

# Local imports
import database
import general_commands
import deathroll_commands

from dotenv import load_dotenv

# Environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PSQL_PASS = os.getenv('PSQL_PASS')

# Discord bot variables
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
db = database.Database(bot, PSQL_PASS)

# Command extensions
bot.add_cog(general_commands.GeneralCommands(bot, db))
bot.add_cog(deathroll_commands.DeathrollCommands(bot, db))


@bot.event
async def on_ready():
    global db

    print('Gambot is connected to Discord.')
    print('Connected to the following guilds :')

    for guild in bot.guilds:
        print(guild.name)

    db.collect_data()


if __name__ == '__main__':
    db.connect()
    print('Connecting Gambot to Discord...')
    bot.run(TOKEN)
