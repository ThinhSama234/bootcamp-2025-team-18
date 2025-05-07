import dotenv from 'dotenv'
dotenv.config();

if (!process.env.DO_SPACES_ENDPOINT) {
  throw new Error('DO_SPACES_ENDPOINT is not defined in .env file');
}

if (!process.env.DO_SPACE_NAME) {
  throw new Error('DO_SPACE_NAME is not defined in .env file');
}

if (!process.env.DO_SPACES_ACCESS_KEY) {
  throw new Error('DO_ACCESS_KEY is not defined in .env file');
}

if (!process.env.DO_SPACES_SECRET) {
  throw new Error('DO_SPACES_SECRET is not defined in .env file');
}

export const DO_SPACES_ENDPOINT = process.env.DO_SPACES_ENDPOINT;
export const DO_SPACE_NAME = process.env.DO_SPACE_NAME;
export const DO_SPACES_ACCESS_KEY = process.env.DO_SPACES_ACCESS_KEY;
export const DO_SPACES_SECRET = process.env.DO_SPACES_SECRET;