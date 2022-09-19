import { GatewayIntentBits, Snowflake } from 'discord-api-types/v10';
import { Awaitable, Client, Collection, Guild, GuildMember, Role } from 'discord.js';
import { settle } from './async';
import { removeUserByThaliaId } from './ddb';
import { MemberWithDiscord, MemberWithRoles } from '../models/member';
import { MemberGroupDetails, MemberGroupType } from '../models/memberGroup';

const { DISCORD_BOT_TOKEN, DISCORD_EXCLUDED_ROLES } = process.env;
const EXCLUDED_ROLES = DISCORD_EXCLUDED_ROLES.split(',');

export const DISCORD_SUPERUSER_ROLE = 'Admin';
export const DISCORD_CONNECTED_ROLE = 'Connected';

export const createClient = async () => {
  return new Promise<Client>((resolve, reject) => {
    try {
      const client = new Client({ intents: [GatewayIntentBits.Guilds] });
      client.once('ready', async () => {
        console.info('Discord client ready.');
        resolve(client);
      });
      client.login(DISCORD_BOT_TOKEN);
    } catch (e) {
      reject(e);
    }
  });
};

export const sendMessageToUser = async (userId: string, message: string, client: Client) => {
  const user = await client.users.fetch(userId);
  await user.send(message);
};

const calculateMemberRoles = (
  inputMembers: Record<string, MemberWithDiscord>,
  memberGroups: MemberGroupDetails[]
): Record<string, MemberWithRoles> => {
  const members = Object.fromEntries(
    Object.entries<MemberWithDiscord>(inputMembers).map(([pk, member]) => {
      if (member.membership_type) {
        member['roles'] = [
          DISCORD_CONNECTED_ROLE,
          member.membership_type
            .split(' ')
            .map((word) => {
              return word[0].toUpperCase() + word.substring(1);
            })
            .join(' ')
        ];
      } else {
        member['roles'] = [];
      }
      return [pk, member as MemberWithRoles];
    })
  );

  for (const memberGroup of memberGroups) {
    for (const groupMembership of memberGroup['members']) {
      const memberPk = groupMembership.member.pk;
      if (memberPk in members && members[memberPk]['membership_type']) {
        if (memberGroup.type == MemberGroupType.COMMITTEE) {
          members[memberPk].roles.push('Committee Member');
        } else if (memberGroup.type == MemberGroupType.SOCIETY) {
          members[memberPk].roles.push('Society Member');
        }
        members[memberPk].roles.push(memberGroup['name']);
      }
    }

    if (memberGroup.chair && memberGroup.chair.pk in members && members[memberGroup.chair.pk].membership_type) {
      if (memberGroup.type == MemberGroupType.COMMITTEE) {
        members[memberGroup.chair.pk].roles.push('Committee Chair');
      } else if (memberGroup.type == MemberGroupType.SOCIETY) {
        members[memberGroup.chair.pk].roles.push('Society Chair');
      }
    }
  }

  return members;
};

const syncRoles = async (thaliaRoles: string[], member: GuildMember, guild: Guild) => {
  const discordRoles = new Collection<string, Role>();

  for (const roleName of thaliaRoles) {
    let discordRole = guild.roles.cache.find((value) => value.name == roleName);
    if (!discordRole) {
      console.info(`Trying to create role ${roleName}`);
      discordRole = await guild.roles.create({ name: roleName });
    }
    discordRoles.set(discordRole.id, discordRole);
  }

  const currentMember = await member.fetch();
  const keepRoles = currentMember.roles.cache.filter((role) => {
    return EXCLUDED_ROLES.includes(role.name);
  });

  return discordRoles.concat(keepRoles);
};

const pruneRoles = (guild: Guild, execute = false) => {
  const removeRoles = guild.roles.cache.filter((role) => {
    return !EXCLUDED_ROLES.includes(role.name) && role.members.size == 0;
  });

  if (execute) {
    removeRoles.forEach((role) => role.delete('Pruning roles'));
  } else {
    console.warn('There are roles to be pruned: ' + removeRoles);
  }
};

const pruneMembers = async (
  members: Record<string, any>,
  guild: Guild,
  nonSyncableRoles: Collection<Snowflake, Role>
) => {
  const discordIds = Object.values(members)
    .map((x) => x.discord)
    .filter(Boolean);
  const discordMembers = guild.members.cache.filter((x) => !discordIds.includes(x.id));
  const edits = [];
  for (const member of discordMembers.values()) {
    if (member.roles.cache.filter((x) => !(x.name in nonSyncableRoles)).size > 0) {
      edits.push(
        member.edit({
          roles: member.roles.cache.intersect(nonSyncableRoles),
          reason: 'Automatic sync'
        })
      );
    }
  }
  await settle(edits);
};

export const syncMembers = async (
  members: Record<string, MemberWithDiscord>,
  memberGroups: MemberGroupDetails[],
  guild: Guild,
  prune = false
) => {
  const membersWithRoles = calculateMemberRoles(members, memberGroups);
  const nonSyncableGuildRoles = guild.roles.cache.filter((role) => EXCLUDED_ROLES.includes(role.name));

  const edits = [];

  for (const member of Object.values(membersWithRoles).filter((value) => value.discord)) {
    try {
      const discordMember =
        guild.members.cache.find((x) => x.id == member.discord) ??
        (await guild.members.fetch(member.discord).catch((reason) => {
          console.error(reason);
          return undefined;
        }));

      if (!discordMember) {
        await removeUserByThaliaId(member.pk);
        continue;
      }

      const roles = await syncRoles(member.roles, discordMember, guild);
      const displayName = member['profile']['display_name'].slice(0, 32);
      if (
        roles.filter((role) => !discordMember.roles.cache.get(role.id) && !nonSyncableGuildRoles.get(role.id)).size > 0 ||
        discordMember.displayName != displayName
      ) {
        console.info(
          `User ${discordMember.id} has new roles`,
          roles.filter((role) => !discordMember.roles.cache.get(role.id) && !nonSyncableGuildRoles.get(role.id))
        );
        edits.push(
          discordMember.edit({
            nick: displayName,
            roles,
            reason: 'Automatic sync'
          })
        );
      }
    } catch (e) {
      console.error(`Syncing member ${member.pk} failed`, e);
    }
  }

  await Promise.allSettled(edits);

  if (prune) {
    console.info('Starting member prune');
    await pruneMembers(membersWithRoles, guild, nonSyncableGuildRoles);
    console.info('Starting role prune');
    await pruneRoles(guild);
  }
};
