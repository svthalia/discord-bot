from discord import Embed
from discord.utils import find, get
from discord.ext import commands

from common.bot_logger import get_logger
from common.helper_functions import reply_and_delete
from common.discord_helper import DISCORD_GUILD_ID, is_connected_or_dm
from common.constants import ThaliaColours

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
        await ctx.send_help(self.group)

    @group.command(help="Outputs all users with the role given in the argument(s)")
    @is_connected_or_dm()
    async def getmembers(self, ctx, *args):
        try:
            roles = get(self.bot.guilds, id=DISCORD_GUILD_ID).roles
            for arg in args:
                if arg.lower() in map(lambda r: r.name.lower(), roles):
                    # get members and pass info
                    # pylint: disable=cell-var-from-loop
                    role = find(lambda r: r.name.lower() == arg.lower(), roles)
                    # pylint: enable=cell-var-from-loop

                    msg = Embed(
                        title=role.name,
                        colour=ThaliaColours.MAGENTA,
                        description="\n".join(
                            [member.display_name for member in role.members]
                        ),
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
                            ctx, f"Group '{arg}' does not have a role in the server."
                        )
                    else:
                        await ctx.author.send(
                            f"Group '{arg}' does not have a role in the server."
                        )
        except:
            logger.exception(
                "Error in getmembers: 'ctx.message.content=%s' by user: 'ctx.author=%s'",
                ctx.message.content,
                ctx.author,
            )
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(GroupCog(bot))
