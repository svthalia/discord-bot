import { createClient } from './common/utils/discord';
import { TextBasedChannel } from 'discord.js';

const main = async () => {
  const client = await createClient();

  const guild = await client.guilds.fetch(process.env.DISCORD_GUILD_ID);
  const channel = (await guild.channels.fetch('774976144763781150')) as TextBasedChannel;

  channel.send(
    'Welcome to the Thalia Discord!\n' +
      '\n' +
      'To get full access to all the channels please connect your Discord account to your Thalia account.\n' +
      "You should use the command '/connect' to do this.\n" +
      '\n' +
      'Not a member (yet)? You can still access a few channels so that you have the ability to ask questions about Thalia (in #boardroom) or this Discord server (in #server-questions).'
  );
};

main();
