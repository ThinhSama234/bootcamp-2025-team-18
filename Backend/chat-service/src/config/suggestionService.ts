import dotenv from 'dotenv';
dotenv.config();

const SUGGESTION_SERVICE_URL = process.env.SUGGESTION_SERVICE_URL;
if (!SUGGESTION_SERVICE_URL) {
  throw new Error('SUGGESTION_SERVICE_URL is not defined');
}

export { 
  SUGGESTION_SERVICE_URL
}