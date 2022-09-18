import { getBackendToken, getMember, getMemberGroups, getMembers } from './utils/thalia-api';
import { getDiscordIdsByThaliaIds } from './utils/ddb';
import { createClient, syncMembers } from './utils/discord';
import { MemberWithDiscord } from './models/member';

export default async (memberId?: string) => {
  console.info('Running sync');
  const accessToken = await getBackendToken();

  const remoteMembers = memberId ? [await getMember(accessToken, memberId)] : await getMembers(accessToken);
  const userPks = remoteMembers.map((member) => member.pk.toString());

  console.info(`Currently ${Object.keys(remoteMembers).length} members on the remote server`);

  const memberGroups = await getMemberGroups(accessToken);

  console.info(`Currently ${memberGroups.length} member groups on the remote server`);

  const userTable = await getDiscordIdsByThaliaIds(userPks);

  console.info(`Currently ${Object.keys(userTable).length} users connected`);

  const members = remoteMembers
    .filter((member) => {
      return !!userTable[member.pk.toString()];
    })
    .reduce<Record<string, MemberWithDiscord>>((acc, member) => {
      acc[member.pk.toString()] = {
        ...member,
        discord: userTable[member.pk.toString()]
      };
      return acc;
    }, {});

  console.log('Connecting to Discord');
  const discordClient = await createClient();
  const guild = await discordClient.guilds.fetch(process.env.DISCORD_GUILD_ID);

  console.info(`Currently ${guild.memberCount} guild members`);

  // await syncMembers(members, memberGroups, guild);

  console.info('Sync complete');
};
