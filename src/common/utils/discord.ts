import { REST } from '@discordjs/rest';
import { Routes } from 'discord-api-types/v10';
// import { Awaitable, Client, ClientEvents } from 'discord.js';

const { DISCORD_BOT_TOKEN } = process.env;

const rest = new REST({ version: '10' }).setToken(DISCORD_BOT_TOKEN);

export const getUser = async (userId: string) => {
  return await rest.get(Routes.user(userId));
};

export const getGuild = async (guildId: string) => {
  return await rest.get(Routes.guild(guildId));
};

// export const createClient = async (onReady?: (client: Client) => Awaitable<void>) => {
//   const client = new Client({ intents: [GatewayIntentBits.Guilds] });
//   client.once('ready', onReady);
//   await client.login(DISCORD_BOT_TOKEN);
//   return client;
// };
//
// export const sendMessageToUser = async (userId: string, message: string, client: Client) => {
//   const user = await client.users.fetch(userId);
//   await user.send(message);
// };
