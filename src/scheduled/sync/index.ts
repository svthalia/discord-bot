import sync from './sync';

export const lambdaHandler = async (): Promise<void> => {
  await sync();
};
