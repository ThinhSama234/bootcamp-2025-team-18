import { Logger } from "./Logger";


export default class LoggerFactory {
  constructor() {
    this._loggers = new Map<string, Logger>();
  }

  register(loggerName: string, logger: Logger): void {
    this._loggers.set(loggerName, logger);
  }

  getLogger(loggerName: string): Logger {
    const logger = this._loggers.get(loggerName);
    if (!logger) {
      throw new Error(`Logger ${loggerName} not found`);
    }

    return logger;
  }

  private _loggers: Map<string, Logger>;
  ;
}