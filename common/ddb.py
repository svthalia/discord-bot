from typing import List, Union

import os
import aioboto3

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from common.bot_logger import get_logger

USERS_TABLE = os.getenv("USERS_TABLE")

logger = get_logger(__name__)


async def write_user(thalia_user_id: Union[str, int], discord_user_id: Union[str, int]):
    async with aioboto3.resource("dynamodb") as dynamodb:
        users_table = await dynamodb.Table(USERS_TABLE)
        response = await users_table.update_item(
            Key={"thalia_user_id": str(thalia_user_id)},
            UpdateExpression="SET discord_user_id = :v",
            ExpressionAttributeValues={
                ":v": str(discord_user_id),
            },
        )
        return response


async def get_user_by_thalia_id(thalia_user_id: Union[str, int]) -> dict:
    async with aioboto3.resource("dynamodb") as dynamodb:
        users_table = await dynamodb.Table(USERS_TABLE)
        try:
            response = await users_table.query(
                KeyConditionExpression=Key("thalia_user_id").eq(str(thalia_user_id))
            )
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
            return None
        else:
            return response["Items"][0] if response["Count"] > 0 else None


async def get_user_by_discord_id(discord_user_id: Union[str, int]) -> dict:
    async with aioboto3.resource("dynamodb") as dynamodb:
        users_table = await dynamodb.Table(USERS_TABLE)
        try:
            response = await users_table.query(
                IndexName="DiscordIndex",
                KeyConditionExpression=Key("discord_user_id").eq(str(discord_user_id)),
            )
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
            return None
        else:
            return response["Items"][0] if response["Count"] > 0 else None


async def get_discord_users_by_thalia_ids(thalia_user_ids: List[str]) -> List[dict]:
    async with aioboto3.resource("dynamodb") as dynamodb:
        users_table = await dynamodb.Table(USERS_TABLE)
        try:
            response = await users_table.scan(
                FilterExpression=Attr("thalia_user_id").is_in(thalia_user_ids)
            )
            data = response["Items"]

            while "LastEvaluatedKey" in response:
                response = await users_table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                data.extend(response["Items"])
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
            return None
        else:
            return data if len(data) > 0 else None
