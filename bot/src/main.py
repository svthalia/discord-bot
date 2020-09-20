import os
import sys
import asyncio
from os.path import dirname, join, abspath

# Add common folder for local machine execution
if os.path.isdir('../common'):
    sys.path.append(abspath(join(dirname(__file__), '../../common/src')))

import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs.greetings import GreetingsCog

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.add_cog(GreetingsCog(bot))

bot.run(TOKEN)
