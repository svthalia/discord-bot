import os
import sys

import discord
from discord.ext import commands

from common.thalia_oauth import get_backend_oauth_client
from common.bot_logger import get_logger
from common.ddb import get_user_by_discord_id
from common.thalia_api import get_member_by_id

logger = get_logger(__name__)

CONNECT_DOMAIN_NAME = f"{os.getenv('DOMAIN_NAME')}start-auth"
MESSAGE_DELETE_AFTER = 10


class WhoAmICog(commands.Cog, name="WhoAmI"):
    def __init__(self, bot):
        self.bot = bot

        logger.info("WhoAmI cog initialised")

    @commands.command()
    async def whoami(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} ({member.id}) sent !whoami")

        try:
            user_data = await get_user_by_discord_id(member.id)

            if user_data:
                member_data = await get_member_by_id(
                    self.bot.thalia_client, user_data["thalia_user_id"]
                )

                await member.send(
                    f"You are {member_data['display_name']}, Thalia member with user ID {user_data['thalia_user_id']}"
                )
            else:
                await member.send(f"You have no associated Thalia user id")
        except Exception as e:
            logger.exception("Error")
            await member.send("Sorry, something went wrong.")

        try:
            await ctx.message.delete()
        except:
            # ignore
            pass

    @commands.command()
    async def connect(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} ({member.id}) sent !connect")

        user_data = await get_user_by_discord_id(member.id)

        await member.send(
            f"Visit {CONNECT_DOMAIN_NAME}?discord-user={member.id} to connect your account",
            delete_after=MESSAGE_DELETE_AFTER,
        )
        if user_data:
            await member.send(
                f"Note: Your Discord tag has already been connected",
                delete_after=MESSAGE_DELETE_AFTER,
            )

        try:
            await ctx.message.delete()
        except:
            # ignore
            pass


def setup(bot):
    bot.add_cog(WhoAmICog(bot))
