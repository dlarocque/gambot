# gambot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    print('Gambot is connected to Discord.')
    print('Connected to the following guilds :')

    for guild in client.guilds:
        print(guild.name)

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content == 'Hey Gambot':
        await message.channel.send(f'Hey {message.author.display_name} :)')
    if message.content == '!github':
        await message.channel.send(f'https://github.com/dlarocque/Gambot')

client.run(TOKEN)
