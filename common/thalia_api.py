import requests
import os
from common.thalia_oauth import get_oauth2_session

THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")


def get_authenticated_member(session):
    return session.get(f"{THALIA_SERVER_URL}api/v1/members/me/").json()


def get_member_by_id(session, user_id):
    return session.get(f"{THALIA_SERVER_URL}api/v1/members/{user_id}/").json()
