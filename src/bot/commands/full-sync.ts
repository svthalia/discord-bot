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
    await ctx.defer();

    try {
      await sync();
    } catch (e) {
      console.error(e);
    }

    await ctx.editOriginal('Sync complete.');
  }
}
