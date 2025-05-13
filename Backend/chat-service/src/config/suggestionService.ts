import dotenv from 'dotenv';
dotenv.config();

if (!process.env.LOCATION_SERVICE_GRPC_URL) {
  throw new Error('SUGGESTION_SERVICE_URL is not defined');
}
const LOCATION_SERVICE_GRPC_URL = process.env.LOCATION_SERVICE_GRPC_URL;

export { 
  LOCATION_SERVICE_GRPC_URL
}