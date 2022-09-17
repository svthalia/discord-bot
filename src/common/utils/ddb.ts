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

export const getUserByThaliaId = async (thaliaUserId: string) => {
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
    return Items[0] ? Items.length > 0 : undefined;
  } catch (e) {
    console.error(e);
  }
};

export const getUserByDiscordId = async (discordUserId: string) => {
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
    return Items[0] ? Items.length > 0 : undefined;
  } catch (e) {
    console.error(e);
  }
};

export const removeUserByThaliaId = async (thaliaUserId: string) => {
  try {
    return dynamoDb.send(
      new DeleteCommand({
        TableName: USERS_TABLE,
        Key: { thalia_user_id: thaliaUserId }
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

  return data.filter((item) => item['thalia_user_id'] in thaliaIds);
};
