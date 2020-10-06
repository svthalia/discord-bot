from discord import Embed
from discord.utils import find
from discord.ext import commands

from common.bot_logger import get_logger
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)


class GroupCog(commands.Cog, name="Group management"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Group cog initialised")

    @commands.group(
        name="group",
        invoke_without_command=True,
        help="Get information about groups",
    )
    async def group(self, ctx):
        await ctx.send("No subcommand was found!")
        await ctx.send_help(self.member)

    @group.command(help="Outputs all users with the role given in the argument(s)")
    async def getmembers(self, ctx, *args):
        try:
            if ctx.guild:
                roles = ctx.guild.roles
                for arg in args:
                    if arg.lower() in map(lambda r: r.name.lower(), roles):
                        # get members and pass info
                        # pylint: disable=cell-var-from-loop
                        role = find(lambda r: r.name.lower() == arg.lower(), roles)
                        # pylint: enable=cell-var-from-loop

                        msg = Embed(title=role.name, colour=0xE62272)
                        for member in role.members:
                            msg.add_field(
                                name="\u200B", value=str(member.nick), inline=True
                            )

                        await ctx.author.send(embed=msg)
                        try:
                            await ctx.message.delete()
                        except:
                            # ignore
                            pass
                    else:
                        if arg == args[0]:
                            await reply_and_delete(
                                ctx,
                                "Group '"
                                + arg
                                + "' does not have a role in the server.",
                            )
                        else:
                            await ctx.author.send(
                                "Group '"
                                + arg
                                + "' does not have a role in the server."
                            )
            else:
                await reply_and_delete(
                    ctx, "This command can only be used in a discord server!"
                )
        except:
            logger.exception(
                "Error in getgroup: 'ctx.message.content=%s' by user: 'ctx.author=%s'",
                ctx.message.content,
                ctx.author,
            )
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(GroupCog(bot))
