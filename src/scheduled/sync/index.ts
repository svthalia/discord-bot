import sync from './sync';

export const lambdaHandler = async (): Promise<void> => {
  console.info('Running sync');
  await sync();
  console.info('Sync complete');
};
