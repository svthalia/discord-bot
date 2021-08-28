import os

THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")
THALIA_API_URL = f"{THALIA_SERVER_URL}api/v1"


async def get_authenticated_member(client):
    response = await client.get(f"{THALIA_API_URL}/members/me/")
    return response.json()


async def get_member_by_id(client, user_id):
    response = await client.get(f"{THALIA_API_URL}/members/{user_id}/")
    return response.json()


async def get_membergroups(client):
    response = await client.get(f"{THALIA_API_URL}/activemembers/groups/")
    return response.json()


async def get_members(client):
    response = await client.get(f"{THALIA_API_URL}/members/")
    return response.json()
