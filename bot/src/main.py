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

from cogs.whoami import WhoAmICog
from cogs.token_refresh import OAuthRefreshCog

from common.bot_logger import get_logger
from common.thalia_oauth import get_backend_oauth_session

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
THALIA_CLIENT_ID = os.getenv("THALIA_CLIENT_ID")
THALIA_CLIENT_SECRET = os.getenv("THALIA_CLIENT_SECRET")
THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")
THALIA_SCOPES = "members:read read"

thalia_client = get_backend_oauth_session()

bot = commands.Bot(command_prefix="!")
logger = get_logger(__name__)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_error(event, *args, **kwargs):
    logger.warning(traceback.format_exc())


bot.add_cog(WhoAmICog(bot, thalia_client))
bot.add_cog(OAuthRefreshCog(bot, thalia_client))

bot.run(TOKEN)
