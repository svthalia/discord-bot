import os
import sys
import traceback

from os.path import dirname, join, abspath, isfile, isdir
from os import listdir

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Add common folder for execution
if isdir("../common"):
    sys.path.append(abspath(join(dirname(__file__), "../../")))


# pylint: disable=wrong-import-position
from core.bot import ThaliaBot
from common.bot_logger import get_logger, configure_logging
from common.helper_functions import reply_and_delete

# pylint: enable=wrong-import-position

configure_logging("bot.log")

COGS_MODULE = "cogs"

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = os.getenv("DISCORD_COMMAND_PREFIX")

bot = ThaliaBot(command_prefix=PREFIX)
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
async def on_error(event_name):
    # pylint: disable=unused-argument
    logger.warning("Ignoring exception: %s", traceback.format_exc())


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
        return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        # pylint: disable=protected-access
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        await reply_and_delete(ctx, "That command does not exist.")
    elif isinstance(error, commands.DisabledCommand):
        await reply_and_delete(ctx, f"{ctx.command} has been disabled.")
    else:
        logger.warning(
            "Ignoring exception in command %s:\n%s",
            ctx.command,
            "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            ),
        )


bot.run(TOKEN)
logger.warning("Bot stopped running")
