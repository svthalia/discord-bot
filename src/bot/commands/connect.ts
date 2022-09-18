import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import { getTokenFromUserId } from '../utils/security';
import { getUserByDiscordId } from '../utils/ddb';

export default class ConnectCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'connect',
      description: 'Connect your Thalia account.'
    });
  }

  async run(ctx: CommandContext) {
    try {
      const discordUser = ctx.member ?? ctx.user;
      const thaliaUserId = await getUserByDiscordId(discordUser.id);
      if (thaliaUserId) {
        return {
          content: 'Your account is already connected.',
          ephemeral: true
        };
      }
      const token = getTokenFromUserId(discordUser.id);
      return {
        content: `Visit ${process.env.DOMAIN_NAME}?discord-user=${token} to connect your Thalia account`,
        ephemeral: true
      };
    } catch (e) {
      console.error(e);
    }
  }
}
