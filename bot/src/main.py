import os
import sys
import asyncio
from os.path import dirname, join, abspath

# Add common folder for execution
if os.path.isdir("../common"):
    sys.path.append(abspath(join(dirname(__file__), "../../")))

from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands

from cogs.greetings import GreetingsCog
from cogs.whoami import WhoAmICog

from common.bot_logger import get_logger

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix="!")
logger = get_logger(__name__)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_error(event, *args, **kwargs):
    logger.warning(traceback.format_exc())


bot.add_cog(GreetingsCog(bot))
bot.add_cog(WhoAmICog(bot))

bot.run(TOKEN)
