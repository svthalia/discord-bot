import asyncio
from discord.ext import commands

from common.bot_logger import get_logger

logger = get_logger(__name__)

class RepoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info("Repo cog initialised")

    @commands.command()
    async def license(self, ctx, *, cog: str):
        await ctx.send("My code is licensed under APGL v3, you can find the full text here: https://github.com/svthalia/discord-bot/blob/master/LICENSE.md")

    @commands.command()
    async def github(self, ctx, *, cog: str):
        await ctx.send("My code can be found here: https://github.com/svthalia/discord-bot")


def setup(bot):
    bot.add_cog(RepoCog(bot))
