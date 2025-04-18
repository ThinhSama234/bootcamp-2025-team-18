import mongoose from "mongoose";
import dotenv from "dotenv";
import logger from "../core/logger";
dotenv.config();

const CHATDB_URL = process.env.CHATDB_URL;
if (!CHATDB_URL) {
  throw new Error("CHATDB_URL is not defined in .env file");
}

const connectDB = async () => {
  try {
    await mongoose.connect(CHATDB_URL);
    logger.info('MongoDB connected');
  } catch (err: any) {
    logger.error('MongoDB connection error: ' + err.message);
    process.exit(1);
  }
};

export default connectDB;