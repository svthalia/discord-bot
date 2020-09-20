import os
import sys

import discord
from discord.ext import commands
from common.bot_logger import get_logger

logger = get_logger(__name__)


class GreetingsCog(commands.Cog, name="Greetings"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logger.info(f"Member joined: {member}")
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("Welcome {0.mention}.".format(member))

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        logger.info(f"{member} sent !hello")
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send("Hello {0.name}~".format(member))
        else:
            await ctx.send("Hello {0.name}... This feels familiar.".format(member))
        self._last_member = member
