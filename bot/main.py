import os
import sys
import traceback

from os.path import dirname, join, abspath, isfile, isdir
from os import listdir

# Add common folder for execution
if isdir("../common"):
    sys.path.append(abspath(join(dirname(__file__), "../../")))

from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands

from core.bot import ThaliaBot

from common.bot_logger import get_logger

COGS_MODULE = "cogs"

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
THALIA_CLIENT_ID = os.getenv("THALIA_CLIENT_ID")
THALIA_CLIENT_SECRET = os.getenv("THALIA_CLIENT_SECRET")
THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")
THALIA_SCOPES = "members:read read"

bot = ThaliaBot(command_prefix="!")
logger = get_logger(__name__)

if __name__ == "__main__":
    cogs_dir = join(dirname(__file__), "cogs")
    for extension in [
        f.replace(".py", "") for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))
    ]:
        try:
            bot.load_extension(f"{COGS_MODULE}.{extension}")
        except Exception as e:
            print(
                f"Failed to load extension {COGS_MODULE}.{extension}.", file=sys.stderr
            )
            traceback.print_exc()


@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_error(event, *args, **kwargs):
    logger.warning(traceback.format_exc())


bot.run(TOKEN)
