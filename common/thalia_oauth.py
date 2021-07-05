import os

from authlib.integrations.httpx_client import AsyncOAuth2Client

from common.bot_logger import get_logger

logger = get_logger(__name__)

CLIENT_ID = os.getenv("THALIA_CLIENT_ID")
CLIENT_SECRET = os.getenv("THALIA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
AUTHORIZE_URL = f'{os.getenv("THALIA_SERVER_URL")}user/oauth/authorize/'
TOKEN_URL = f'{os.getenv("THALIA_SERVER_URL")}user/oauth/token/'


def _update_token():
    logger.info("Received new access token for API client")


def get_oauth2_client(token=None):
    return AsyncOAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope="members:read activemembers:read",
        redirect_uri=REDIRECT_URI,
        code_challenge_method="S256",
        token=token,
        update_token=_update_token,
    )


async def get_backend_oauth_client():
    client = AsyncOAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope="read members:read activemembers:read",
        redirect_uri=REDIRECT_URI,
        code_challenge_method="S256",
        update_token=_update_token,
    )
    token = await client.fetch_token(TOKEN_URL, grant_type="client_credentials")
    return client
