import dotenv from 'dotenv';
dotenv.config();

import BuiltInLogger from "./BuiltInLogger";
import LoggerFactory from "./LoggerFactory";
import FileOutputStream from "../stream/FileOutputStream";
import ConsoleOutputStream from "../stream/ConsoleOutputStream";

const IS_PRODUCTION_MODE = process.env.NODE_ENV === 'production';

const loggerFactory = new LoggerFactory();

enum LoggerType {
  BUILT_IN = 'built-in',
};

const builtInLogger = new BuiltInLogger(
  IS_PRODUCTION_MODE 
    ? new FileOutputStream('logs/server_log.logs') 
    : new ConsoleOutputStream()
);
loggerFactory.register(LoggerType.BUILT_IN, builtInLogger);


export default loggerFactory.getLogger(LoggerType.BUILT_IN);
