import asyncio
from discord.ext import commands
from discord import Activity, ActivityType

from common.bot_logger import get_logger

logger = get_logger(__name__)


class InfoCog(commands.Cog, name="Bot Information"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Info cog initialised")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.watching, name="!help for docs"),
            status="!help for docs",
        )

    @commands.group(
        name="info",
        invoke_without_command=True,
        help="Gives you information about this bot",
    )
    async def info(self, ctx):
        await ctx.send(
            "I am a Discord Bot maintained by Thalia's Technicie. My code is licensed under APGL v3 and completely open source.\n"
            "You can find my source code here: https://github.com/svthalia/discord-bot\n\n"
            "Use the command `!info version` to check my current revision."
        )

    @info.command()
    async def version(self, ctx):
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD", stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Current git revision is {stdout.decode()}")


def setup(bot):
    bot.add_cog(InfoCog(bot))
