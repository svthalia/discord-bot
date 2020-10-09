import asyncio
from typing import Optional

from discord import User, utils
from discord.ext import commands

from common.bot_logger import get_logger
from common.discord_helper import DISCORD_GUILD_ID, DISCORD_SUPERUSER_ROLE
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)


class ManageCog(commands.Cog, name="Bot management"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Manage cog initialised")

    @commands.group(name="manage", hidden=True, invoke_without_command=True)
    async def manage(self, ctx):
        await ctx.send("No subcommand was found!")
        await ctx.send_help(self.manage)

    @manage.command(help="Toggle the Admin role for you or a mentioned user")
    @commands.is_owner()
    async def su(self, ctx, user: Optional[User]):
        user = user or ctx.author
        guild = utils.get(self.bot.guilds, id=DISCORD_GUILD_ID)
        member = utils.get(guild.members, id=user.id)
        role = utils.get(guild.roles, name=DISCORD_SUPERUSER_ROLE)

        if utils.get(member.roles, id=role.id):
            await member.remove_roles(*[role])
            await reply_and_delete(
                ctx, f"Removed the {DISCORD_SUPERUSER_ROLE} role from <@{member.id}>"
            )
        else:
            await member.add_roles(*[role])
            await reply_and_delete(
                ctx, f"Added the {DISCORD_SUPERUSER_ROLE} role to <@{member.id}>"
            )

    @manage.command(help="Load a module from the cogs in the repository")
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module"""

        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @manage.command(help="Unload a module from the cogs in the repository")
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module"""

        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @manage.command(help="Reload a module from the cogs in the repository")
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module"""

        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @manage.command(help="git fetch && git reset --hard origin/master")
    @commands.is_owner()
    async def pull(self, ctx):
        try:
            await asyncio.create_subprocess_exec("git", "fetch")
            await asyncio.create_subprocess_exec(
                "git", "reset", "--hard", "origin/master"
            )
            proc = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD", stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Current git revision is {stdout.decode()}")

    @manage.command(help="Closes the current version of the bot")
    @commands.is_owner()
    async def restart(self, ctx):
        try:
            await self.bot.close()
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @manage.command(
        help="Announce something in a channel. The complete string after the channel name will be used as message. That includes newlines.",
    )
    @commands.is_owner()
    async def announce(self, _, channel: str, *, message: str):
        guild = utils.get(self.bot.guilds, id=DISCORD_GUILD_ID)
        channel = utils.get(guild.channels, name=channel)
        await channel.send(message)


def setup(bot):
    bot.add_cog(ManageCog(bot))
