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


def _calculate_member_roles(members, membergroups):
    for member in members.values():
        if members[member["pk"]]["membership_type"]:
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


async def _calculate_roles(thalia_roles, member, guild):
    discord_roles = set()

    for role_name in thalia_roles:
        discord_role = discord.utils.get(guild.roles, name=role_name)
        if not discord_role:
            discord_role = await guild.create_role(name=role_name)
        discord_roles.add(discord_role)

    keep_roles = {role for role in member.roles if role.name in EXCLUDES_ROLES}

    return discord_roles | keep_roles


async def _prune_roles(guild):
    remove_roles = [
        role
        for role in guild.roles
        if role.name not in EXCLUDES_ROLES and len(role.members) == 0
    ]
    for role in remove_roles:
        await role.delete()


async def _prune_members(members, guild):
    non_syncable_guild_roles = [
        role for role in guild.roles if role.name in EXCLUDES_ROLES
    ]

    discord_ids = list(
        filter(
            lambda x: x is not None, map(lambda x: x.get("discord"), members.values())
        )
    )
    discord_members = filter(lambda x: x.id not in discord_ids, guild.members)
    for member in discord_members:
        try:
            await member.edit(
                roles=set(member.roles) & set(non_syncable_guild_roles),
                reason="Automatic sync",
            )
        except:
            logger.exception("Error syncing a member, %s", str(member))


async def sync_members(members, membergroups, guild):
    members = _calculate_member_roles(members, membergroups)

    for member in filter(lambda x: x.get("discord"), members.values()):
        discord_user = guild.get_member(member["discord"])
        if not discord_user:
            discord_user = await guild.fetch_member(member["discord"])
        try:
            roles = await _calculate_roles(member["roles"], discord_user, guild)
            await discord_user.edit(
                nick=member["display_name"], roles=roles, reason="Automatic sync"
            )
        except:
            logger.exception("Error syncing a member, %s", member["display_name"])

    await _prune_members(members, guild)
    await _prune_roles(guild)
