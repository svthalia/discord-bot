import { APIGatewayProxyEventV2, APIGatewayProxyResult } from 'aws-lambda';
import base64url from 'base64url';
import crypto from 'crypto';

export const lambdaHandler = async (event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResult> => {
  const { DISCORD_GUILD_ID, OAUTH_REDIRECT_URI, THALIA_CLIENT_ID, THALIA_SERVER_URL } = process.env;

  const discordUser = event.queryStringParameters ? event.queryStringParameters['discord-user'] : undefined;
  if (!discordUser) {
    return {
      statusCode: 302,
      body: `Missing discord user.`,
      headers: {
        Location: `https://discord.com/channels/${DISCORD_GUILD_ID}`
      }
    };
  }

  const state = crypto.randomBytes(8).toString('hex');
  const codeVerifier = crypto.pseudoRandomBytes(64).toString('hex');
  const codeChallenge = base64url.encode(crypto.createHash('sha256').update(codeVerifier).digest());

  const cookieValue = base64url.encode(JSON.stringify({ discord_user: discordUser, code_verifier: codeVerifier }));

  const authorizationUrl =
    `${THALIA_SERVER_URL}user/oauth/authorize/?` +
    `client_id=${THALIA_CLIENT_ID}` +
    '&response_type=code' +
    `&state=${state}` +
    `&code_challenge=${codeChallenge}` +
    '&code_challenge_method=S256' +
    '&scope=profile:read members:read activemembers:read' +
    `&redirect_uri=${OAUTH_REDIRECT_URI}`;

  return {
    statusCode: 302,
    headers: {
      Location: authorizationUrl,
      'Set-Cookie': `${state}=${cookieValue}; Path=/complete-auth; Secure; Max-Age: 600;`
    },
    body: `You should now be redirect to ${authorizationUrl}`
  };
};
