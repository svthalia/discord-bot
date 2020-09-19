import requests
import os
from thalia_oauth import get_oauth2_session

THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")


def get_authenticated_member(access_token):
    session = get_oauth2_session(access_token)
    return session.get(f"{THALIA_SERVER_URL}api/v1/members/me/").json()


def get_member_by_id(access_token, user_id):
    session = get_oauth2_session(access_token)
    return session.get(f"{THALIA_SERVER_URL}api/v1/members/{user_id}/").json()
