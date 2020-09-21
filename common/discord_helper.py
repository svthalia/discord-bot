import os
from discord import Client

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")


async def get_client():
    client = Client()
    await client.login(DISCORD_BOT_TOKEN)
    return client


async def sync_member(discord_user_id, user_data, guild):
    member = await guild.fetch_member(discord_user_id)

    await member.edit(nick=user_data["display_name"])

    return member
