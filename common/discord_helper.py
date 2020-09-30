import os
import discord
from discord import Client

from common.bot_logger import get_logger

logger = get_logger(__name__)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
EXCLUDES_ROLES = set(
    ["Superadmin", "Admin", "Moderator", "@everyone", "Thalia Bot", "Thalia Test Bot"]
)


async def get_client():
    client = Client()
    await client.login(DISCORD_BOT_TOKEN)
    return client


def _calculate_roles(members, membergroups):
    for member in members.values():
        members[member["pk"]]["roles"] = {
            "Connected",
            members[member["pk"]]["membership_type"].capitalize(),
        }

    for membergroup in membergroups:
        for group_member in membergroup["members"]:
            if group_member["pk"] in members:
                if membergroup["type"] == "committee":
                    members[group_member["pk"]]["roles"].add("Committee Member")
                elif membergroup["type"] == "society":
                    members[group_member["pk"]]["roles"].add("Society Member")
                members[group_member["pk"]]["roles"].add(membergroup["name"])

        if (
            membergroup["type"] == "committee"
            and membergroup["chair"]
            and membergroup["chair"]["pk"] in members
        ):
            members[membergroup["chair"]["pk"]]["roles"].add("Committee Chair")
        elif (
            membergroup["type"] == "society"
            and membergroup["chair"]
            and membergroup["chair"]["pk"] in members
        ):
            members[membergroup["chair"]["pk"]]["roles"].add("Society Chair")

    return members


async def _sync_roles(thalia_roles, member, guild):
    discord_roles = []

    for role_name in thalia_roles:
        discord_role = discord.utils.get(guild.roles, name=role_name)
        if not discord_role:
            discord_role = await guild.create_role(name=role_name)
        discord_roles.append(discord_role)

    syncable_guild_roles = [
        role for role in guild.roles if role.name not in EXCLUDES_ROLES
    ]
    add_roles = list(set(discord_roles) - set(member.roles))
    remove_roles = list(set(syncable_guild_roles) - set(discord_roles))

    await member.add_roles(*add_roles, reason="Automatic sync")
    await member.remove_roles(*remove_roles, reason="Automatic sync")


async def _prune_roles(guild):
    syncable_guild_roles = [
        role for role in guild.roles if role.name not in EXCLUDES_ROLES
    ]
    remove_roles = [role for role in syncable_guild_roles if len(role.members) == 0]
    for role in remove_roles:
        await role.delete()


async def sync_members(members, membergroups, guild):
    members = _calculate_roles(members, membergroups)

    for member in filter(lambda x: x.get("discord"), members.values()):
        discord_user = guild.get_member(member["discord"])
        if not discord_user:
            discord_user = await guild.fetch_member(member["discord"])
        try:
            await _sync_roles(member["roles"], discord_user, guild)
            await discord_user.edit(nick=member["display_name"])
        except:
            logger.exception("Error syncing a member")

    await _prune_roles(guild)
