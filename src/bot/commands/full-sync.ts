import { SlashCommand, SlashCreator, CommandContext } from 'slash-create';
import { getBackendToken, getMemberGroups, getMembers } from '../utils/thalia-api';
import { getDiscordIdsByThaliaIds } from '../utils/ddb';
import { createClient, syncMembers } from '../utils/discord';
import { MemberWithDiscord } from '../../common/models/member';

const { DISCORD_GUILD_ID } = process.env;

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

    const accessToken = await getBackendToken();

    const members = (await getMembers(accessToken)).reduce((acc, member) => {
      acc[member.pk] = member;
      return acc;
    }, {});
    const memberGroups = await getMemberGroups(accessToken);
    const userTable = await getDiscordIdsByThaliaIds(Object.keys(members));

    for (const record of userTable) {
      members[record['thalia_user_id']]['discord'] = record['discord_user_id'];
    }

    const discordClient = await createClient();
    const guild = await discordClient.guilds.fetch(DISCORD_GUILD_ID);

    const filteredMembers = Object.fromEntries<MemberWithDiscord>(
      Object.entries<MemberWithDiscord>(members).filter(([, val]) => val['discord'])
    );

    await syncMembers(filteredMembers, memberGroups, guild);

    await ctx.editOriginal('Sync complete.');
  }
}
