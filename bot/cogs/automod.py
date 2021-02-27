import re

from discord.ext import commands

from common.bot_logger import get_logger

logger = get_logger(__name__)


class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checks = {"discord\.gg\/[A-z]+": self.discord_invite}
        logger.info("AutoMod cog initialised")

    @commands.Cog.listener()
    async def on_message(self, message):
        for check, func in self.checks.items():
            if re.search(check, message.content) is not None:
                await func(message)

    async def discord_invite(self, message):
        await message.delete()
        await message.author.send("No Discord invites please.")


def setup(bot):
    bot.add_cog(AutoModCog(bot))
