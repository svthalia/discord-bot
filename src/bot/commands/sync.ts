import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import sync from '../sync';
import { getUserByDiscordId } from '../utils/ddb';

export default class SyncCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'sync',
      description: 'Syncs your Discord account to the Thalia website.',
      throttling: {
        usages: 1,
        duration: 900
      }
    });
  }

  async run(ctx: CommandContext) {
    await ctx.defer(true);
    const name = ctx.member.displayName ?? ctx.user.username;

    const thaliaUserId = await getUserByDiscordId(ctx.user.id);
    if (thaliaUserId) {
      await sync(thaliaUserId);

      return {
        content: `Syncing ${name}!`,
        ephemeral: true
      };
    } else {
      return {
        content: `Not connected!`,
        ephemeral: true
      };
    }
  }
}
