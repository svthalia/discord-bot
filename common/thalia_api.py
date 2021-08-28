import os
import math
import asyncio
from common.bot_logger import get_logger
from .helper_functions import gather_with_concurrency

logger = get_logger(__name__)

THALIA_SERVER_URL = os.getenv("THALIA_SERVER_URL")
THALIA_API_URL = f"{THALIA_SERVER_URL}api/v2"


async def get_authenticated_member(client):
    response = await client.get(f"{THALIA_API_URL}/members/me/")
    return response.json()


async def get_member_by_id(client, user_id):
    response = await client.get(f"{THALIA_API_URL}/members/{user_id}/")
    return response.json()


async def get_membergroups(client):
    groups = await _get_paginated_results(client, f"{THALIA_API_URL}/activemembers/groups/")
    coros = [_get_individual_group(client, group["pk"]) for group in groups]
    return await gather_with_concurrency(2, *coros)


async def get_members(client):
    return await _get_paginated_results(client, f"{THALIA_API_URL}/members/")


async def _get_paginated_results(client, url):
    location = f"{url}?limit=100"

    response = await client.get(location)
    data = response.json()

    if not "results" in data:
        logger.info("No results in response: %s", data)
        return []

    results = data["results"]

    if data["count"] > 100:
        num = math.ceil(data["count"] / 100)

        async def get_next(url, i):
            response = await client.get(f"{url}?limit=100&offset={100*i}")
            data = response.json()
            if not "results" in data:
                logger.info("No results in response: %s", data)
                return []
            return data["results"]

        coros = [get_next(url, i) for i in range(1, num)]
        more_results = await asyncio.gather(*coros)

        results += [item for sublist in more_results for item in sublist]

    return results


async def _get_individual_group(client, pk):
    response = await client.get(f"{THALIA_API_URL}/activemembers/groups/{pk}/")
    data = response.json()
    data["chair"] = None
    try:
        if data["members"]:
            chair_membership = next(filter(lambda x: x["chair"], data["members"]))
            data["chair"] = chair_membership["member"]
    except StopIteration:
        logger.info("No chair found for %s", data["name"])
    return data
