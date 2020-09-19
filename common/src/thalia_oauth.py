from requests_oauthlib import OAuth2Session
import os

client_id = os.getenv("THALIA_CLIENT_ID")
client_secret = os.getenv("THALIA_CLIENT_SECRET")
redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
authorize_url = f'{os.getenv("THALIA_SERVER_URL")}user/oauth/authorize/'
token_url = f'{os.getenv("THALIA_SERVER_URL")}user/oauth/token/'

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def get_oauth2_session(access_token=None):
    return OAuth2Session(
        client_id,
        scope="read members:read",
        redirect_uri=redirect_uri,
        token=access_token,
    )
