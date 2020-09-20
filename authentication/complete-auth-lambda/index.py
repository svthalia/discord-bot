import os
import requests
import json
import base64
from common.thalia_oauth import exchange_code
from common.thalia_api import get_authenticated_member
from common.ddb import write_user

DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")


def lambda_handler(event, context):
    # try:
    session = get_oauth_session(event)
    member_data = get_authenticated_member(session)
    write_user(member_data["pk"], discord_user)
    # except Exception as e:
    #     return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

    # TODO: Probably start sync for the user here?

    return {
        "statusCode": 302,
        "headers": {"Location": f"https://discord.com/channels/{DISCORD_GUILD_ID}"},
        "body": json.dumps({}),
    }


def get_oauth_session(event):
    code = event["queryStringParameters"].get("code", None)
    state_key = event["queryStringParameters"].get("state", None)

    cookies = {}
    for cookie in event.get("cookies", []):
        values = cookie.split("=")
        cookies[values[0]] = "=".join(values[1:])

    if not code:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Code not found in request"}),
        }

    if not state_key:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "State not found in request"}),
        }

    state_value = cookies.get(state_key, None)

    if not state_value:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "State cookie not found"}),
        }

    state_value = base64.urlsafe_b64decode(state_value.encode()).decode()

    return exchange_code(code)
