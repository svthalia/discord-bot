import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import { getTokenFromUserId } from '@common/security';
import { getUserByDiscordId } from '@common/ddb';

export default class ConnectCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'connect',
      description: 'Connect your Thalia account.'
    });
  }

  async run(ctx: CommandContext) {
    try {
      const user = await getUserByDiscordId(ctx.member.id);
      if (user) {
        return {
          content: 'Your account is already connected.',
          ephemeral: true
        };
      }
      const token = getTokenFromUserId(ctx.member.id);
      return {
        content: `Visit ${process.env.DOMAIN_NAME}?discord-user=${token} to connect your Thalia account`,
        ephemeral: true
      };
    } catch (e) {
      console.error(e);
    }
  }
}
