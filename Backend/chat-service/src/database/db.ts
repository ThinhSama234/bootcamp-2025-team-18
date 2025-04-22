import mongoose from "mongoose";
import logger from "../core/logger";
import { CHATDB_URL } from "../config/db";


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