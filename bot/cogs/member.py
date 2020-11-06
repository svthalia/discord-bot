import os

from discord.ext import commands

from common.discord_helper import get_user_token_from_id
from common.bot_logger import get_logger
from common.ddb import get_user_by_discord_id
from common.thalia_api import get_member_by_id
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)

CONNECT_DOMAIN_NAME = f"{os.getenv('DOMAIN_NAME')}"


class MemberCog(commands.Cog, name="Member management"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Member cog initialised")

    @commands.group(
        name="member",
        invoke_without_command=True,
        help="Get information about your connection to the Thalia website",
    )
    async def member(self, ctx):
        await ctx.send("No subcommand was found!")
        await ctx.send_help(self.member)

    @member.command(help="Outputs your current display name and user id")
    async def whoami(self, ctx):
        try:
            user_data = await get_user_by_discord_id(ctx.author.id)

            if user_data:
                member_data = await get_member_by_id(
                    self.bot.thalia_client, user_data["thalia_user_id"]
                )

                await reply_and_delete(
                    ctx,
                    f"You are {member_data['display_name']}, Thalia member with user ID {user_data['thalia_user_id']}",
                )
            else:
                await reply_and_delete(ctx, "You have no associated Thalia user id")
        except:
            logger.exception(
                "Error: Could not send 'whoami' information to 'ctx.author=%s'",
                ctx.author,
            )
            await reply_and_delete(ctx, "Sorry, something went wrong.")

    @member.command(help="Gives info on how to connect your Discord and Thalia account")
    async def connect(self, ctx):
        user_data = await get_user_by_discord_id(ctx.author.id)

        if user_data:
            await reply_and_delete(
                ctx, "Your Discord tag has already been connected"
            )
            return

        token = get_user_token_from_id(ctx.author.id)
        await reply_and_delete(
            ctx,
            f"Visit {CONNECT_DOMAIN_NAME}?discord-user={token} to connect your Thalia account",
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        token = get_user_token_from_id(member.id)
        await member.send(
            f"Welcome to the Thalia Discord! Visit {CONNECT_DOMAIN_NAME}?discord-user={token} to connect your Thalia account"
        )


def setup(bot):
    bot.add_cog(MemberCog(bot))
