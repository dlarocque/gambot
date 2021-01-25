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

# not working
@client.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if channel.name == 'general':
            await client.send_message(channel, f'''{member.name}, welcome to my Discord Server!\n
            I will be keeping track of your interactions with other members
            of the server and award you points accordingly!  \nFor more
            information on what you can with those points, type !help in
            the discord channel!\n
            Have fun!''')

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content == 'Hey Gambot':
        await message.channel.send(f'Hey {message.author.nick} :)')
    if message.content == '!github':
        await message.channel.send(f'https://github.com/dlarocque/Gambot')

client.run(TOKEN)
