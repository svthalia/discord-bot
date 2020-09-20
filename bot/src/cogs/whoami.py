import os
import sys

import discord
from discord.ext import commands
from bot_logger import get_logger

from ddb import get_user_by_discord_id

logger = get_logger(__name__)

CONNECT_DOMAIN_NAME = f"{os.getenv('DOMAIN_NAME')}start-auth"
MESSAGE_DELETE_AFTER = 5


class WhoAmICog(commands.Cog, name="WhoAmI"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whoami(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} ({member.id}) sent !whoami")

        user_data = get_user_by_discord_id(member.id)

        if user_data:
            await ctx.send(
                f"Your Thalia user id is {user_data['thalia_user_id']}",
                delete_after=MESSAGE_DELETE_AFTER,
            )
        else:
            await ctx.send(
                f"You have no associated Thalia user id",
                delete_after=MESSAGE_DELETE_AFTER,
            )

        await ctx.message.delete(delay=MESSAGE_DELETE_AFTER)

    @commands.command()
    async def connect(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} ({member.id}) sent !whoami")

        user_data = get_user_by_discord_id(member.id)

        if user_data:
            await ctx.send(
                f"Your Discord tag has already been connected",
                delete_after=MESSAGE_DELETE_AFTER,
            )
        else:
            await ctx.send(
                f"Visit {CONNECT_DOMAIN_NAME}?discord-user={member.id} to connect your account",
                delete_after=MESSAGE_DELETE_AFTER,
            )

        await ctx.message.delete(delay=MESSAGE_DELETE_AFTER)
