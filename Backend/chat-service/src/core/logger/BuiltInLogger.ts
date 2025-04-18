import { Logger } from "./Logger";
import ConsoleOutputStream from "../stream/ConsoleOutputStream";
import OutputStream from "../stream/OutputStream";

const COLOR_MAP = {
  trace: '\x1b[36m',
  info: '\x1b[32m',
  warn: '\x1b[33m',
  error: '\x1b[31m',
  debug: '\x1b[34m',
};

export const DEFAULT_FMT = '[%l][%t] %s';

export type LogLevel = 'trace' | 'info' | 'warn' | 'error' | 'debug';

/**
 * 
 * %t - timestamp
 * %l - log level
 * %s - message
 */
export default class BuiltInLogger implements Logger {

  constructor(stream: OutputStream = new ConsoleOutputStream(), fmt: string = DEFAULT_FMT) {
    this._ostream = stream;
    this._fmt = fmt;
  }

  setFormat(fmt: string): void {
    this._fmt = fmt;
  }

  trace(message: string): void {
    this._ostream
      .setColor(COLOR_MAP.trace)
      .write(this._format('trace', message));
  }

  info(message: string): void {
    this._ostream
      .setColor(COLOR_MAP.info)
      .write(this._format('info', message));
  }

  warn(message: string): void {
    this._ostream
      .setColor(COLOR_MAP.warn)  
      .write(this._format('warn', message));
  }

  error(message: string): void {
    this._ostream
      .setColor(COLOR_MAP.error)
      .write(this._format('error', message));
  }

  debug(message: string): void {
    this._ostream
      .setColor(COLOR_MAP.debug)
      .write(this._format('debug', message));
  }

  private _format(level: LogLevel, message: string): string {
    return this._fmt
      .replace('%l', level)
      .replace('%t', new Date().toLocaleTimeString())
      .replace('%s', message)
  }

  private _fmt: string;
  private _ostream: OutputStream;
}