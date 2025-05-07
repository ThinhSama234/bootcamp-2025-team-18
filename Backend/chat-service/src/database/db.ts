import mongoose from "mongoose";
import logger from "../core/logger";
import { CHATDB_URL, DB_NAME } from "../config/db";


const connectDB = async () => {
  try {
    await mongoose.connect(CHATDB_URL, {
      dbName: DB_NAME,
    });
    
    logger.info('MongoDB connected');
  } catch (err: any) {
    logger.error('MongoDB connection error: ' + err.message);
    process.exit(1);
  }
};

export default connectDB;