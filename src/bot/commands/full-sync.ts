import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import sync from '../sync';

export default class FullSyncCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'full-sync',
      description: 'Syncs all users.',
      requiredPermissions: ['MANAGE_GUILD']
    });
  }

  async run(ctx: CommandContext) {
    await ctx.defer(true);

    await sync();

    await ctx.editOriginal('Sync complete.');

    return 'Sync complete.';
  }
}
