from datetime import datetime

from discord import utils
from discord.ext import tasks, commands

from common.bot_logger import get_logger
from common.discord_helper import DISCORD_GUILD_ID, DISCORD_CONNECTED_ROLE

logger = get_logger(__name__)


class ThaliaNightCog(commands.Cog, name=""):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Thalia Night cog initialised")
        self.check_availability.start()

    def cog_unload(self):
        self.check_availability.cancel()

    @tasks.loop(seconds=60)
    async def check_availability(self):
        now = datetime.now()

        guild = utils.get(self.bot.guilds, id=DISCORD_GUILD_ID)
        thalia_night_category = utils.get(guild.categories, name="Thalia Night")

        if thalia_night_category is None:
            return

        role = utils.get(guild.roles, name=DISCORD_CONNECTED_ROLE)
        role_overwrites = thalia_night_category.overwrites.get(role)

        channels_available = (
            now.weekday() == 2 and now.hour >= 19 or now.weekday() == 3 and now.hour < 5
        )

        if role_overwrites.view_channel != channels_available:
            logger.info(
                f"Changed Thalia Night category visibility to {channels_available}"
            )
            await thalia_night_category.set_permissions(
                role, view_channel=channels_available
            )

            if guild.public_updates_channel:
                await guild.public_updates_channel.send(
                    f"Changed Thalia Night category visibility to {channels_available}"
                )

    @check_availability.before_loop
    async def before_check_availability(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(ThaliaNightCog(bot))
