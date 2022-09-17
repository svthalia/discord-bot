import { GatewayIntentBits, Snowflake } from 'discord-api-types/v10';
import { Awaitable, Client, Collection, Guild, GuildMember, Role } from 'discord.js';
import { settle } from './async';
import { removeUserByThaliaId } from './ddb';
import { Member } from '../models/member';
import { MemberGroupDetails } from '../models/memberGroup';

const { DISCORD_BOT_TOKEN, DISCORD_EXCLUDED_ROLES } = process.env;
const EXCLUDED_ROLES = DISCORD_EXCLUDED_ROLES.split(',');

export const createClient = async (onReady?: (client: Client) => Awaitable<void>) => {
  const client = new Client({ intents: [GatewayIntentBits.Guilds] });
  client.once('ready', onReady ?? (() => {}));
  console.log(DISCORD_BOT_TOKEN);
  await client.login(DISCORD_BOT_TOKEN);
  return client;
};

export const sendMessageToUser = async (userId: string, message: string, client: Client) => {
  const user = await client.users.fetch(userId);
  await user.send(message);
};

const calculateMemberRoles = (members: Record<string, Member>, memberGroups: MemberGroupDetails[]) => {
  for (const member of Object.values(members)) {
    if (member['membership_type']) {
      members[member['pk']]['roles'] = [
        'Connected',
        members[member['pk']]['membership_type']
          .split(' ')
          .map((word) => {
            return word[0].toUpperCase() + word.substring(1);
          })
          .join(' ')
      ];
    } else {
      members[member['pk']]['roles'] = [];
    }
  }

  for (const memberGroup of memberGroups) {
    for (const groupMembership of memberGroup['members']) {
      const memberPk = groupMembership.member.pk;
      if (memberPk in members && members[memberPk]['membership_type']) {
        if (memberGroup['type'] == 'committee') {
          members[memberPk]['roles'].push('Committee Member');
        } else if (memberGroup['type'] == 'society') {
          members[memberPk]['roles'].push('Society Member');
        }
        members[memberPk]['roles'].push(memberGroup['name']);
      }
    }

    if (
      memberGroup['chair'] &&
      memberGroup['chair']['pk'] in members &&
      members[memberGroup['chair']['pk']]['membership_type']
    ) {
      if (memberGroup['type'] == 'committee') {
        members[memberGroup['chair']['pk']]['roles'].push('Committee Chair');
      } else if (memberGroup['type'] == 'society') {
        members[memberGroup['chair']['pk']]['roles'].push('Society Chair');
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
      discordRole = await guild.roles.create({ name: roleName });
    }
    discordRoles.set(discordRole.id, discordRole);
  }

  const keepRoles = member.roles.cache.filter((role) => {
    return role.name in EXCLUDED_ROLES;
  });

  return discordRoles.concat(keepRoles);
};

const pruneRoles = (guild: Guild, execute = false) => {
  const removeRoles = guild.roles.cache.filter((role) => {
    return !(role.name in EXCLUDED_ROLES) && role.members.size == 0;
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
  const discordMembers = guild.members.cache.filter((x) => !(x.id in discordIds));
  const edits = [];
  for (const member of discordMembers.values()) {
    if (member.roles.cache.filter((x) => !(x.name in nonSyncableRoles)).size > 0) {
      edits.push(
        member.edit({
          roles: member.roles.cache.concat(nonSyncableRoles),
          reason: 'Automatic sync'
        })
      );
    }
  }
  await settle(edits);
};

export const syncMembers = async (
  members: Record<string, Member>,
  memberGroups: MemberGroupDetails[],
  guild: Guild,
  prune = false
) => {
  const membersWithRoles = calculateMemberRoles(members, memberGroups);
  const nonSyncableGuildRoles = guild.roles.cache.filter((role) => role.name in EXCLUDED_ROLES);

  const edits = [];
  for (const member of Object.values(membersWithRoles).filter((value) => value['discord'])) {
    const discordMember =
      guild.members.cache.find((member) => member.id == member['discord']) ??
      (await guild.members.fetch(member['discord']));
    if (!discordMember) {
      return removeUserByThaliaId(member['pk']);
    }

    const roles = await syncRoles(member['roles'], discordMember, guild);
    const displayName = member['profile']['display_name'].slice(0, 32);
    if (
      roles
        .filter((role) => !!discordMember.roles.cache.find((memberRole) => role.id == memberRole.id))
        .difference(nonSyncableGuildRoles).size > 0 ||
      discordMember.displayName != displayName
    ) {
      edits.push(
        discordMember.edit({
          nick: displayName,
          roles,
          reason: 'Automatic sync'
        })
      );
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
