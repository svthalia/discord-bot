import discord
from discord.ext import commands
from common.thalia_oauth import get_backend_oauth_client


class ThaliaBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thalia_client = None

    async def connect(self, *args, **kwargs):
        self.thalia_client = await get_backend_oauth_client()
        await super().connect(*args, **kwargs)
        await self.change_presence(
            activity=discord.CustomActivity(name="!help for docs"),
            status="!help for docs",
        )
