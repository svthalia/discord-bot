from discord.ext.commands import DefaultHelpCommand


class ThaliaHelpCommand(DefaultHelpCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, dm_help=True, **kwargs)

    async def prepare_help_command(self, ctx, command):
        try:
            await ctx.message.delete()
        except:
            # ignore
            pass
        await super().prepare_help_command(ctx, command)
