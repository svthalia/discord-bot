import asyncio
import json
import base64
import secrets
from common.thalia_oauth import get_oauth2_client, AUTHORIZE_URL
from common.discord_helper import DISCORD_GUILD_ID

loop = asyncio.get_event_loop()


async def async_handle(event):
    try:
        client = get_oauth2_client()

        discord_user = event.get("queryStringParameters", {}).get("discord-user", None)
        if not discord_user:
            return {
                "statusCode": 302,
                "headers": {"Location": f"https://discord.com/channels/{DISCORD_GUILD_ID}"},
                "body": "Missing discord user.",
            }

        random = secrets.token_bytes(64)
        code_verifier = base64.b64encode(random, b"-_").decode().replace("=", "")

        cookie_value = base64.urlsafe_b64encode(
            json.dumps(
                {"discord_user": discord_user, "code_verifier": code_verifier}
            ).encode()
        ).decode()

        authorization_url, state = client.create_authorization_url(
            AUTHORIZE_URL, grant_type="authorization_code", code_verifier=code_verifier
        )

        return {
            "statusCode": 302,
            "headers": {
                "Location": authorization_url,
                "Set-Cookie": f"{state}={cookie_value}; Secure; Max-Age: 600;",
            },
            "body": f"You should now be redirect to {authorization_url}",
        }
    except Exception as e:
        return {"statusCode": 400, "body": str(e)}


def lambda_handler(event, _):
    return loop.run_until_complete(async_handle(event))
