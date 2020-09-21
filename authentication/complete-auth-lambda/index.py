import json
import base64
import asyncio
from common.thalia_oauth import get_oauth2_client, TOKEN_URL
from common.thalia_api import get_authenticated_member
from common.ddb import write_user
from common.discord_helper import get_client, sync_member, DISCORD_GUILD_ID
from common.bot_logger import get_logger

loop = asyncio.get_event_loop()
logger = get_logger(__name__)


async def async_handle(event):
    try:
        state = get_event_state(event)
        client = get_oauth2_client()

        logger.debug(f"State info: {state}")

        await client.fetch_token(
            TOKEN_URL,
            authorization_response=f"{event.get('rawPath')}?{event.get('rawQueryString')}",
            code_verifier=state["code_verifier"],
            grant_type="authorization_code",
        )

        member_data = await get_authenticated_member(client)

        logger.debug(f"Member data: {member_data}")

        await write_user(member_data["pk"], state["discord_user"])

        try:
            discord_client = await get_client()
            guild = await discord_client.fetch_guild(DISCORD_GUILD_ID)
            await sync_member(state["discord_user"], member_data, guild)
        except Exception as e:
            logger.exception("Error during Discord sync")

        return {
            "statusCode": 302,
            "headers": {"Location": f"https://discord.com/channels/{DISCORD_GUILD_ID}"},
            "body": "You can close this tab now.",
        }
    except Exception as e:
        logger.exception("Error during execution")
        return {
            "statusCode": 400,
            "body": f"Error: {str(e)}",
        }


def get_event_state(event):
    state_key = event["queryStringParameters"].get("state", None)
    cookies = {}
    for cookie in event.get("cookies", []):
        values = cookie.split("=")
        cookies[values[0]] = "=".join(values[1:])

    state_value = cookies.get(state_key, None)

    if not state_value:
        raise Exception("State cookie not found")

    state_value = json.loads(base64.urlsafe_b64decode(state_value.encode()).decode())

    return state_value


def lambda_handler(event):
    return loop.run_until_complete(async_handle(event))
