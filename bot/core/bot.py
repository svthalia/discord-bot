from discord.ext import commands
from common.thalia_oauth import get_backend_oauth_client
from .help import ThaliaHelpCommand


class ThaliaBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thalia_client = None
        self.help_command = ThaliaHelpCommand()

    async def connect(self, *args, **kwargs):
        self.thalia_client = await get_backend_oauth_client()
        await super().connect(*args, **kwargs)
