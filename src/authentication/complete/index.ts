import { APIGatewayProxyEventV2, APIGatewayProxyResult } from 'aws-lambda';
import base64url from 'base64url';
import { getUserIdFromToken } from './utils/security';
import Undici from 'undici';
import { getAuthenticatedMember } from './utils/thalia_api';
import { saveUser } from './utils/ddb';
// import { createClient, sendMessageToUser } from './discord';

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

  const thaliaData = await getAuthenticatedMember(responseBody.access_token);

  console.log('saving user');

  await saveUser(thaliaData['pk'].toString(), state['discord_user']);

  // const discordClient = await createClient();
  // await sendMessageToUser(
  //   state['discord_user'],
  //   `Your account has been connected. Welcome to the Thalia Discord ${thaliaData['display_name']}!`,
  //   discordClient
  // );

  console.log('saved user');

  return {
    statusCode: 302,
    headers: { Location: `https://discord.com/channels/${DISCORD_GUILD_ID}` },
    body: 'You can close this tab now.'
  };
  //   try:
  //   state = get_event_state(event)
  //   state["discord_user"] = get_user_id_from_token(state["discord_user"])
  //   client = get_oauth2_client()
  //
  //   logger.debug(f"State info: {state}")
  //
  //   await client.fetch_token(
  //     TOKEN_URL,
  //     authorization_response=f"{event.get('rawPath')}?{event.get('rawQueryString')}",
  //     code_verifier=state["code_verifier"],
  //     grant_type="authorization_code",
  // )
  //
  //   thalia_data = await get_authenticated_member(client)
  //
  //   logger.debug(f"Member data: {thalia_data}")
  //
  //   await write_user(thalia_data["pk"], state["discord_user"])
  //
  //   try:
  //   discord_client = await get_client()
  //   guild = await discord_client.fetch_guild(DISCORD_GUILD_ID)
  //   member = await guild.fetch_member(state["discord_user"])
  //   thalia_data["discord"] = state["discord_user"]
  //   membergroups = await get_membergroups(client)
  //
  //   await sync_members({thalia_data["pk"]: thalia_data}, membergroups, guild)
  //
  //   await member.send(
  //     f"Your account has been connected. Welcome to the Thalia Discord {thalia_data['display_name']}!"
  // )
  //   except Exception:
  //     logger.exception("Error during Discord sync")
  //   return {
  //     "statusCode": 400,
  //     "body": f"Error: {str(e)}",
  //   }
  //
  //   return {
  //     "statusCode": 302,
  //     "headers": {"Location": f"https://discord.com/channels/{DISCORD_GUILD_ID}"},
  //     "body": "You can close this tab now.",
  //   }
  //   except Exception as e:
  //   logger.exception("Error during execution")
  //   return {
  //     "statusCode": 400,
  //     "body": f"Error: {str(e)}",
  //   }
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
