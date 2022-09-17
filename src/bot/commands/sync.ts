import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import sync from '../sync';

export default class SyncCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'sync',
      description: 'Syncs your Discord account to the Thalia website.'
    });
  }

  async run(ctx: CommandContext) {
    const name = ctx.member.displayName ?? ctx.user.username;
    await sync();
    return {
      content: `Sync ${name}!`,
      ephemeral: true
    };
  }
}
