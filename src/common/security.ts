import crypto from 'crypto';

const algorithm = 'aes-256-cbc';
const key = crypto.createHash('sha256').update(process.env.DISCORD_BOT_TOKEN).digest();

export const getUserIdFromToken = (token: string) => {
  return decrypt(JSON.parse(Buffer.from(token, 'base64').toString()));
};

export const getTokenFromUserId = (userId: string) => {
  return Buffer.from(JSON.stringify(encrypt(userId))).toString('base64');
};

const encrypt = (data: string): { iv: string; content: string } => {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  const encrypted = Buffer.concat([cipher.update(data), cipher.final()]);
  return {
    iv: iv.toString('base64'),
    content: encrypted.toString('base64')
  };
};

const decrypt = (data: { iv: string; content: string }): string => {
  const decipher = crypto.createDecipheriv(algorithm, key, Buffer.from(data.iv, 'base64'));
  const decrypted = Buffer.concat([decipher.update(data.content, 'base64'), decipher.final()]);
  return decrypted.toString();
};
