import asyncio
from discord.ext import tasks, commands
from common.thalia_oauth import refresh_backend_oauth_session
from common.bot_logger import get_logger

logger = get_logger(__name__)

class OAuthRefreshCog(commands.Cog):
    def __init__(self, bot, thalia_client):
        self.bot = bot
        self.thalia_client = thalia_client
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5)
    async def printer(self):
        logger.info(f"Refresh token: {self.thalia_client.get('refresh_token')}")
        self.thalia_client = await refresh_backend_oauth_session(self.thalia_client)

    @printer.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()
        logger.info(f"Refresh token: {self.thalia_client.token.get('refresh_token')}")