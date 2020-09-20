import os
import sys

import discord
from discord.ext import commands
from bot_logger import get_logger

from ddb import get_user_by_discord_id

logger = get_logger(__name__)

CONNECT_DOMAIN_NAME = f"{os.getenv('DOMAIN_NAME')}start-auth"


class WhoAmICog(commands.Cog, name="WhoAmI"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whoami(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} ({member.id}) sent !whoami")

        user_data = get_user_by_discord_id(member.id)

        if user_data:
            await member.send(
                f"Your Thalia user id is {user_data['thalia_user_id']}"
            )
        else:
            await member.send(
                f"You have no associated Thalia user id"
            )

        try:
            await ctx.message.delete()
        except:
            # ignore
            pass

    @commands.command()
    async def connect(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} ({member.id}) sent !whoami")

        user_data = get_user_by_discord_id(member.id)

        if user_data:
            await member.send(
                f"Your Discord tag has already been connected"
            )
        else:
            await member.send(
                f"Visit {CONNECT_DOMAIN_NAME}?discord-user={member.id} to connect your account"
            )

        try:
            await ctx.message.delete()
        except:
            # ignore
            pass
