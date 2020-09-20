import requests
import json
import base64
from common.thalia_oauth import get_oauth2_session, AUTHORIZE_URL


def lambda_handler(event, context):
    try:
        session = get_oauth2_session()

        discord_user = event.get("queryStringParameters", {}).get("discord-user", None)
        if not discord_user:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing discord user"}),
            }

        cookie_value = base64.urlsafe_b64encode(discord_user.encode()).decode()

        authorization_url, state = session.authorization_url(AUTHORIZE_URL)

        return {
            "statusCode": 302,
            "headers": {
                "Location": authorization_url,
                "Set-Cookie": f"{state}={cookie_value}; Secure; Max-Age: 600;",
            },
            "body": json.dumps({}),
        }
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
