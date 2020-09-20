from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
import os

CLIENT_ID = os.getenv("THALIA_CLIENT_ID")
CLIENT_SECRET = os.getenv("THALIA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
AUTHORIZE_URL = f'{os.getenv("THALIA_SERVER_URL")}user/oauth/authorize/'
TOKEN_URL = f'{os.getenv("THALIA_SERVER_URL")}user/oauth/token/'

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = "read members:read"

def get_oauth2_session(access_token=None):
    return OAuth2Session(
        CLIENT_ID,
        scope=SCOPES,
        redirect_uri=REDIRECT_URI,
        token=access_token,
    )

def exchange_code(code):
    token_data = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        },
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
    ).json()
    return get_oauth2_session(token_data)

def get_backend_oauth_session():
    client = BackendApplicationClient(client_id=CLIENT_ID)
    session = OAuth2Session(client=client)
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    session.fetch_token(token_url=TOKEN_URL, auth=auth)
    return session

def refresh_backend_oauth_session(session):
    print(session.token.get("refresh_token"))
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    session.refresh_token(TOKEN_URL, refresh_token=session.token.get("refresh_token"), auth=auth)
    return session