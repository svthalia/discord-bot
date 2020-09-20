import boto3
import os

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from common.bot_logger import get_logger

USERS_TABLE = os.getenv("USERS_TABLE")

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table(USERS_TABLE)

logger = get_logger(__name__)


def write_user(thalia_user_id, discord_user_id):
    response = users_table.update_item(
        Key={
            'thalia_user_id': str(thalia_user_id)
        },
        UpdateExpression="SET discord_user_id = :v",
        ExpressionAttributeValues={
            ':v': str(discord_user_id),
        }
    )
    return response


def get_user_by_thalia_id(thalia_user_id):
    try:
        response = users_table.query(
            KeyConditionExpression=Key("thalia_user_id").eq(str(thalia_user_id))
        )
    except ClientError as e:
        logger.error(e.response["Error"]["Message"])
        return None
    else:
        return response["Items"][0] if response["Count"] > 0 else None


def get_user_by_discord_id(discord_user_id):
    try:
        response = users_table.query(
            IndexName="DiscordIndex",
            KeyConditionExpression=Key("discord_user_id").eq(str(discord_user_id)),
        )
    except ClientError as e:
        logger.error(e.response["Error"]["Message"])
        return None
    else:
        return response["Items"][0] if response["Count"] > 0 else None
