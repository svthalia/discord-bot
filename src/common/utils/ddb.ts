import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DeleteCommand, DynamoDBDocumentClient, QueryCommand, ScanCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';

const { USERS_TABLE } = process.env;
const ddbClient = new DynamoDBClient({});
const dynamoDb = DynamoDBDocumentClient.from(ddbClient);

export const saveUser = async (thaliaUserId: string, discordUserId: string) => {
  try {
    await dynamoDb.send(
      new UpdateCommand({
        TableName: USERS_TABLE,
        Key: { thalia_user_id: thaliaUserId },
        UpdateExpression: 'SET discord_user_id = :v',
        ExpressionAttributeValues: {
          ':v': discordUserId
        }
      })
    );
  } catch (e) {
    console.error(e);
  }
};

export const getUserByThaliaId = async (thaliaUserId: string): Promise<string> => {
  try {
    const { Items } = await dynamoDb.send(
      new QueryCommand({
        TableName: USERS_TABLE,
        KeyConditionExpression: 'thalia_user_id = :v',
        ExpressionAttributeValues: {
          ':v': thaliaUserId
        }
      })
    );
    return Items[0]['discord_user_id'];
  } catch (e) {
    console.error(e);
  }
};

export const getUserByDiscordId = async (discordUserId: string): Promise<string> => {
  try {
    const { Items } = await dynamoDb.send(
      new QueryCommand({
        TableName: USERS_TABLE,
        IndexName: 'DiscordIndex',
        KeyConditionExpression: 'discord_user_id = :v',
        ExpressionAttributeValues: {
          ':v': discordUserId
        }
      })
    );
    return Items[0]['thalia_user_id'];
  } catch (e) {
    console.error(e);
  }
};

export const removeUserByThaliaId = async (thaliaUserId: number) => {
  try {
    return dynamoDb.send(
      new DeleteCommand({
        TableName: USERS_TABLE,
        Key: { thalia_user_id: thaliaUserId.toString() }
      })
    );
  } catch (e) {
    console.error(e);
  }
};

export const getDiscordIdsByThaliaIds = async (thaliaIds: string[]) => {
  let response = await dynamoDb.send(
    new ScanCommand({
      TableName: USERS_TABLE
    })
  );

  let data = response['Items'];

  while (response.LastEvaluatedKey) {
    response = await dynamoDb.send(
      new ScanCommand({
        TableName: USERS_TABLE,
        ExclusiveStartKey: response.LastEvaluatedKey
      })
    );

    data = data.concat(response['Items']);
  }

  return data
    .filter((item) => {
      return !!thaliaIds.find((value) => value.toString() === item['thalia_user_id'].toString());
    })
    .reduce<Record<string, string>>((acc, item) => {
      acc[item['thalia_user_id']] = item['discord_user_id'];
      return acc;
    }, {});
};
