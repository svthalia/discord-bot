import random
from typing import Optional

from discord.ext import commands

from common.bot_logger import get_logger
from common.discord_helper import is_connected_or_dm

logger = get_logger(__name__)


class DiceCog(commands.Cog, name="Pseudo random values as a service"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Dice cog initialised")

    @commands.command(help="Throw some dice", aliases=["mexx"])
    @is_connected_or_dm()
    async def dice(self, ctx, amount: Optional[int] = 2, eyes: Optional[int] = 6):
        await ctx.send(
            " and ".join([str(random.randint(1, eyes)) for x in range(amount)])
        )

    @commands.command(hidden=True)
    @is_connected_or_dm()
    async def mexxx(self, ctx):
        choices = ["1", "2"]
        random.shuffle(choices)
        await ctx.send(" and ".join(choices))


def setup(bot):
    bot.add_cog(DiceCog(bot))
