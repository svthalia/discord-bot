import aioboto3
import os

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from common.bot_logger import get_logger

USERS_TABLE = os.getenv("USERS_TABLE")

logger = get_logger(__name__)


async def write_user(thalia_user_id, discord_user_id):
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


async def get_user_by_thalia_id(thalia_user_id):
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


async def get_user_by_discord_id(discord_user_id):
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
