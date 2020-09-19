import boto3
import os

USERS_TABLE = os.getenv("USERS_TABLE")

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table(USERS_TABLE)


def write_user(thalia_user_id, discord_user_id):
    response = users_table.put_item(
        Item={
            "thalia_user_id": str(thalia_user_id),
            "discord_user_id": str(discord_user_id),
        }
    )
    return response


def get_user_by_thalia_id(thalia_user_id):
    response = users_table.query(
        KeyConditionExpression=Key("thalia_user_id").eq(str(thalia_user_id))
    )
    return response


def get_user_by_discord_id(discord_user_id):
    response = users_table.query(
        IndexName="DiscordIndex",
        KeyConditionExpression=Key("discord_user_id").eq(str(discord_user_id)),
    )
    return response
