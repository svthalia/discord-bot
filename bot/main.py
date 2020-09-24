import os
import sys
import traceback

from os.path import dirname, join, abspath, isfile, isdir
from os import listdir

from dotenv import load_dotenv

load_dotenv()

# Add common folder for execution
if isdir("../common"):
    sys.path.append(abspath(join(dirname(__file__), "../../")))


# pylint: disable=wrong-import-position
from core.bot import ThaliaBot
from common.bot_logger import get_logger, configure_logging

# pylint: enable=wrong-import-position

configure_logging("bot.log")

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


# pylint: disable=unused-argument
@bot.event
async def on_error(event_name):
    logger.warning(traceback.format_exc())


# pylint: enable=unused-argument


bot.run(TOKEN)
logger.warning("Bot stopped running")
