import { APIGatewayProxyEventV2, APIGatewayProxyResult } from 'aws-lambda';
import base64url from 'base64url';
import { getUserIdFromToken } from './utils/security';
import Undici from 'undici';
import { getAuthenticatedMember, getMemberGroups } from './utils/thalia-api';
import { saveUser } from './utils/ddb';
import { createClient, sendMessageToUser, syncMembers } from './utils/discord';
import { MemberWithDiscord } from '../../common/models/member';

export const lambdaHandler = async (event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResult> => {
  const { DISCORD_GUILD_ID, OAUTH_REDIRECT_URI, THALIA_CLIENT_ID, THALIA_CLIENT_SECRET, THALIA_SERVER_URL } =
    process.env;

  if (!event.queryStringParameters) {
    return {
      statusCode: 400,
      body: 'No query parameters.'
    };
  }

  const state = getState(event);
  state['discord_user'] = getUserIdFromToken(state['discord_user']);

  const response = await Undici.request(`${THALIA_SERVER_URL}user/oauth/token/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json; charset=UTF-8'
    },
    body:
      `grant_type=authorization_code&` +
      `redirect_uri=${OAUTH_REDIRECT_URI}&` +
      `code=${event.queryStringParameters['code']}&` +
      `code_verifier=${state['code_verifier']}&` +
      `client_id=${THALIA_CLIENT_ID}&` +
      `client_secret=${THALIA_CLIENT_SECRET}`
  });

  const responseBody = await response.body.json();
  const accessToken = responseBody.access_token;

  const thaliaData: MemberWithDiscord = {
    ...(await getAuthenticatedMember(accessToken)),
    discord: state['discord_user']
  };

  console.log('Saving user', thaliaData);

  await saveUser(thaliaData['pk'].toString(), state['discord_user']);

  const discordClient = await createClient();
  await sendMessageToUser(
    state['discord_user'],
    `Your account has been connected. Welcome to the Thalia Discord ${thaliaData['profile']['display_name']}!`,
    discordClient
  );

  const memberGroups = await getMemberGroups(accessToken);

  const guild = await discordClient.guilds.fetch(DISCORD_GUILD_ID);
  await syncMembers({ [`${thaliaData['pk']}`]: thaliaData }, memberGroups, guild);

  return {
    statusCode: 302,
    headers: { Location: `https://discord.com/channels/${DISCORD_GUILD_ID}` },
    body: 'You can close this tab now.'
  };
};

const getState = (event: APIGatewayProxyEventV2) => {
  const stateKey = event.queryStringParameters['state'];
  const cookies = {};
  for (const cookie of event.cookies) {
    const values = cookie.split('=');
    cookies[values[0]] = values.slice(1).join('=');
  }

  const stateValue = cookies[stateKey];
  if (!stateValue) {
    throw Error('State cookie not found');
  }

  return JSON.parse(base64url.decode(stateValue));
};
