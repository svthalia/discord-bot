import os
import asyncio
import base64
import discord
from discord import Client, utils
from discord.ext import commands

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from common.ddb import remove_user
from common.bot_logger import get_logger
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
EXCLUDES_ROLES = set(os.getenv("DISCORD_EXCLUDED_ROLES", "").split(","))
DISCORD_SUPERUSER_ROLE = "Admin"
DISCORD_CONNECTED_ROLE = "Connected"


async def get_client():
    client = Client()
    await client.login(DISCORD_BOT_TOKEN)
    return client


def _get_fernet_key():
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(DISCORD_BOT_TOKEN.encode("utf-8"))
    return base64.urlsafe_b64encode(digest.finalize())


def get_user_token_from_id(user_id: int):
    f = Fernet(_get_fernet_key())
    return f.encrypt(f"{user_id}".encode("utf-8")).decode("utf-8")


def get_user_id_from_token(token: str):
    f = Fernet(_get_fernet_key())
    return f.decrypt(f"{token}".encode("utf-8")).decode("utf-8")


async def _edit_member(discord_user, **kwargs):
    try:
        await discord_user.edit(**kwargs)
    except:
        logger.exception("Error editing a guild member: %s", str(discord_user))


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


async def _prune_members(members, guild, non_syncable_guild_roles):
    discord_ids = list(
        filter(
            lambda x: x is not None, map(lambda x: x.get("discord"), members.values())
        )
    )
    discord_members = filter(lambda x: x.id not in discord_ids, guild.members)
    edits = []
    for member in discord_members:
        if len(set(member.roles) - set(non_syncable_guild_roles)) > 0:
            edits.append(
                _edit_member(
                    member,
                    roles=set(member.roles) & set(non_syncable_guild_roles),
                    reason="Automatic sync",
                )
            )
    await asyncio.gather(*edits)


async def sync_members(members, membergroups, guild, prune=False):
    members = _calculate_member_roles(members, membergroups)

    non_syncable_guild_roles = [
        role for role in guild.roles if role.name in EXCLUDES_ROLES
    ]

    edits = []
    for member in filter(lambda x: x.get("discord"), members.values()):
        discord_user = guild.get_member(member["discord"])

        if not discord_user:
            try:
                discord_user = await guild.fetch_member(member["discord"])
            except discord.errors.NotFound:
                # This user is not a member of the guild, remove reference from database
                await remove_user(member["pk"])
                continue

        roles = await _calculate_roles(member["roles"], discord_user, guild)
        if (
            len((set(roles) ^ set(discord_user.roles)) - set(non_syncable_guild_roles))
            > 0
            or discord_user.display_name != member["display_name"][:32]
        ):
            edits.append(
                _edit_member(
                    discord_user,
                    nick=member["display_name"][:32],
                    roles=roles,
                    reason="Automatic sync",
                )
            )
    await asyncio.gather(*edits)

    if prune:
        logger.info("Starting member prune")
        await _prune_members(members, guild, non_syncable_guild_roles)
        logger.info("Starting role prune")
        await _prune_roles(guild)


def is_connected_or_dm():
    async def predicate(ctx):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            role = discord.utils.get(ctx.author.roles, name=DISCORD_CONNECTED_ROLE)
            if role is None:
                await reply_and_delete(
                    ctx, "You do not have access to execute this command."
                )
                return False
        return True

    return commands.check(predicate)


def get_member_list(ctx, args):
    members = []
    not_found = ""
    for arg in args:
        member = ctx.guild.get_member_named(arg)
        if member:
            members.append(member)
        else:
            not_found += arg + ", "
    return members, not_found


async def string_to_role(ctx, name):
    role = utils.get(ctx.guild.roles, name=name)
    if not role:
        await reply_and_delete(ctx, "Could not find role " + name)
    else:
        return role
