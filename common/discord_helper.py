import os
import discord
from discord import Client

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
EXCLUDES_ROLES = set(["admin", "moderator", "@everyone", "Thalia Bot", "Thalia Test Bot"])

async def get_client():
    client = Client()
    await client.login(DISCORD_BOT_TOKEN)
    return client


def _calculate_roles(user_data):
    is_committee_chair = False
    is_society_chair = False

    active_achievements = filter(lambda x: x['latest'] is None and x['active'], user_data["achievements"])
    active_societies = filter(lambda x: x['latest'] is None and x['active'], user_data["societies"])
    roles = set()

    if user_data['membership_type']:
        roles.add(user_data['membership_type'])

    for achievement in active_achievements:
        if 'Board' not in achievement['name']:
            is_committee_chair = achievement['periods'][-1]["chair"]
        roles.add(achievement['name'])

    for society in active_societies:
        is_society_chair = society['periods'][-1]["chair"]
        roles.add(society['name'])

    if is_committee_chair:
        roles.add("Committee Chair")
    if is_society_chair:
        roles.add("Society Chair")

    return roles

async def _sync_roles(user_data, member, guild):
    thalia_roles = _calculate_roles(user_data)
    discord_roles = []

    for role_name in thalia_roles:
        discord_role = discord.utils.get(guild.roles, name=role_name)
        if not discord_role:
            discord_role= await guild.create_role(name=role_name)
        discord_roles.append(discord_role)

    syncable_guild_roles = [role for role in guild.roles if role.name not in EXCLUDES_ROLES]
    add_roles = list(set(discord_roles) - set(member.roles))
    remove_roles = list(set(syncable_guild_roles) - set(discord_roles))

    await member.add_roles(*add_roles)
    await member.remove_roles(*remove_roles)

async def _prune_roles(guild):
    syncable_guild_roles = [role for role in guild.roles if role.name not in EXCLUDES_ROLES]
    remove_roles = [role for role in syncable_guild_roles if len(role.members) == 0]
    for role in remove_roles:
        await role.delete()

async def sync_member(user_data, member, guild):
    await _sync_roles(user_data, member, guild)
    await _prune_roles(guild)
    
    await member.edit(nick=user_data["display_name"])

    return member
