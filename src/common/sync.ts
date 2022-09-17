import { getBackendToken, getMemberGroups, getMembers } from './utils/thalia-api';
import { getDiscordIdsByThaliaIds } from './utils/ddb';
import { createClient, syncMembers } from './utils/discord';
import { MemberWithDiscord } from './models/member';

export default async () => {
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
  const guild = await discordClient.guilds.fetch(process.env.DISCORD_GUILD_ID);

  const filteredMembers = Object.fromEntries<MemberWithDiscord>(
    Object.entries<MemberWithDiscord>(members).filter(([, val]) => val['discord'])
  );

  await syncMembers(filteredMembers, memberGroups, guild);
};
