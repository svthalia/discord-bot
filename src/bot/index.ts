import dotenv from 'dotenv';
import { SlashCreator, AWSLambdaServer } from 'slash-create';
import path from 'path';

let dotenvPath = path.join(process.cwd(), '.env');
if (path.parse(process.cwd()).name === 'dist') dotenvPath = path.join(process.cwd(), '..', '.env');

dotenv.config({ path: dotenvPath });

const creator = new SlashCreator({
  applicationID: process.env.DISCORD_APP_ID,
  publicKey: process.env.DISCORD_PUBLIC_KEY,
  token: process.env.DISCORD_BOT_TOKEN
});

creator.on('debug', (message) => console.log(message));
creator.on('warn', (message) => console.warn(message));
creator.on('error', (error) => console.error(error));
creator.on('rawREST', (request) => {
  console.log('Request:', JSON.stringify(request.body));
});

creator
  .withServer(new AWSLambdaServer(module.exports, 'lambdaHandler'))
  .registerCommandsIn(path.join(__dirname, 'commands'));
