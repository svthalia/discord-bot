from discord import HTTPException
from discord.ext import commands
from common.bot_logger import get_logger
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)


class PurgeCog(commands.Cog, name="Purge command"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Purge cog initialized")

    @commands.has_permissions(manage_messages=True)
    @commands.command(
        help="Removes the amount of messages specified in the argument."
    )
    async def purge(self, ctx, amount: int):
        if 0 < amount <= 100:
            try:
                deleted = await ctx.channel.purge(limit=amount + 1)
                await ctx.channel.send("Deleted {} message(s)".format(len(deleted)-1))
            except HTTPException:
                await reply_and_delete(ctx, "Could not purge messages.")
        else:
            await reply_and_delete(
                ctx,
                "The amount of messages must be more than 0 and less than or equal to 100.",
            )


def setup(bot):
    bot.add_cog(PurgeCog(bot))
