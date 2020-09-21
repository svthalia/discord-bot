import asyncio
from discord.ext import commands

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module"""

        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module"""

        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="reload", hidden=True)
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

    @commands.command(name="version", hidden=True)
    @commands.is_owner()
    async def version(self, ctx):
        try:
            proc = await asyncio.create_subprocess_exec("git", "rev-parse", "HEAD", stdout=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send(f"**`SUCCESS`**: Current git revision is {stdout.decode()}")

    @commands.command(name="pull", hidden=True)
    @commands.is_owner()
    async def pull(self, ctx):
        try:
            await asyncio.create_subprocess_exec("git", "fetch")
            await asyncio.create_subprocess_exec("git", "reset", "--hard", "origin/master")
            proc = await asyncio.create_subprocess_exec("git", "rev-parse", "HEAD", stdout=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send(f"**`SUCCESS`**: Current git revision is {stdout.decode()}")

    @commands.command(name="restart", hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        try:
            await self.bot.close()
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")


def setup(bot):
    bot.add_cog(OwnerCog(bot))
