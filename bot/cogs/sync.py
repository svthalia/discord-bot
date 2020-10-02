import os

import discord
from discord.ext import commands, tasks

from common.bot_logger import get_logger
from common.ddb import get_user_by_discord_id, get_discord_users_by_thalia_ids
from common.thalia_api import get_member_by_id, get_members, get_membergroups
from common.discord_helper import DISCORD_GUILD_ID, sync_members
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)

CONNECT_DOMAIN_NAME = f"{os.getenv('DOMAIN_NAME')}"


class SyncCog(commands.Cog, name="Syncing"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Sync cog initialised")

    @commands.Cog.listener()
    async def on_ready(self):
        self.auto_full_sync.start()

    def cog_unload(self):
        self.auto_full_sync.cancel()

    @commands.group(
        name="sync",
        invoke_without_command=True,
        help="Sync your roles and nickname with the Thalia website",
    )
    async def sync(self, ctx):
        try:
            user_data = await get_user_by_discord_id(ctx.author.id)

            if user_data:
                member = await get_member_by_id(
                    self.bot.thalia_client, user_data["thalia_user_id"]
                )
                member["discord"] = ctx.author.id
                membergroups = await get_membergroups(self.bot.thalia_client)

                guild = discord.utils.get(self.bot.guilds, id=DISCORD_GUILD_ID)

                await sync_members({member["pk"]: member}, membergroups, guild)
                await reply_and_delete(
                    ctx, "Your user data has been synced successfully"
                )
            else:
                await reply_and_delete(ctx, "You have no connected Thalia account")
        except:
            logger.exception(
                "Error: Could not 'sync', invoked by: 'ctx.author=%s'", ctx.author
            )
            await reply_and_delete(ctx, "Sorry, something went wrong.")

    async def _full_sync(self):
        guild = discord.utils.get(self.bot.guilds, id=DISCORD_GUILD_ID)

        members = {
            member["pk"]: member for member in await get_members(self.bot.thalia_client)
        }
        membergroups = await get_membergroups(self.bot.thalia_client)

        user_table = await get_discord_users_by_thalia_ids(
            [str(m) for m in members.keys()]
        )

        for record in user_table:
            members[int(record["thalia_user_id"])]["discord"] = int(
                record["discord_user_id"]
            )

        await sync_members(members, membergroups, guild)

    @tasks.loop(minutes=30)
    async def auto_full_sync(self):
        logger.info("Running periodic member sync")
        await self._full_sync()

    @commands.is_owner()
    @sync.command(name="full", help="Triggers a full sync of all members", hidden=True)
    async def fullsync(self, ctx):
        await reply_and_delete(ctx, "Full sync triggered")
        await self._full_sync()


def setup(bot):
    bot.add_cog(SyncCog(bot))
