import os
import math

THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")
THALIA_API_URL = f"{THALIA_SERVER_URL}api/v2"


async def get_authenticated_member(client):
    response = await client.get(f"{THALIA_API_URL}/members/me/")
    return response.json()


async def get_member_by_id(client, user_id):
    response = await client.get(f"{THALIA_API_URL}/members/{user_id}/")
    return response.json()


async def get_membergroups(client):
    groups = _get_paginated_results(f"{THALIA_API_URL}/activemembers/groups/")
    coros = [_get_individual_group(group["pk"]) for group in groups]
    return asyncio.gather(*coros)


async def get_members(client):
    return _get_paginated_results(f"{THALIA_API_URL}/members/")


async def _get_paginated_results(client, url):
    location = f"{url}?limit=100"

    response = await client.get(location)
    data = response.json()

    if data["count"] > 100:
        num = math.ceil(data["count"] / 100)

        async def get_next(url, i):
            response = await client.get(f"{url}?limit=100&offset={100*i}")
            data = response.json()
            return data["results"]

        coros = [get_next(url, i) for i in range(1, num)]
        more_data = await asyncio.gather(*coros)

        data += [item for sublist in more_data for item in sublist]

    return data


async def _get_individual_group(pk):
    response = await client.get(f"{THALIA_API_URL}/activemembers/groups/{pk}")
    data = response.json()
    chairs = filter(lambda x: x["chair"], data["members"])
    if len(chairs) > 0:
        data["chair"] = chair[0]
    return data