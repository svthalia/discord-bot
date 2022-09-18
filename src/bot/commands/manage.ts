import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import { createClient, DISCORD_SUPERUSER_ROLE } from '../utils/discord';
import { Team } from 'discord.js';

export default class ManageCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'su',
      description: 'Allows you to manage this bot.'
    });
  }

  async run(ctx: CommandContext) {
    await ctx.defer(true);

    const userId = ctx.member?.id ?? ctx.user.id;
    const name = ctx.member.displayName ?? ctx.user.username;

    const client = await createClient();
    const app = await client.application.fetch();

    const isOwner = (app.owner as Team).members.some((member) => member.id === userId);

    if (isOwner) {
      const guild = await client.guilds.fetch(process.env.DISCORD_GUILD_ID);
      const member = await guild.members.fetch(userId);
      const superUserRole = guild.roles.cache.find((role) => role.name === DISCORD_SUPERUSER_ROLE);
      if (member.roles.highest.id === superUserRole.id) {
        await member.roles.remove(superUserRole);

        return {
          content: `Made ${name} non-admin.`,
          ephemeral: true
        };
      } else {
        await member.roles.add(superUserRole);

        return {
          content: `Made ${name} admin.`,
          ephemeral: true
        };
      }
    }

    return {
      content: `No access!`,
      ephemeral: true
    };
  }
}
