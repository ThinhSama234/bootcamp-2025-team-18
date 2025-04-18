import { Request, Response, NextFunction } from 'express';
import { RequestError } from '../responses/ErrorResponse.js';
import { DomainCode } from '../responses/DomainCode.js';
import logger from '../logger/index.js';

const errorHandler = (
  err: Error,
  _req: Request,
  res: Response,
  _next: NextFunction,
) => {
  logger.error(`ERROR HANDLER:\n ${err}`);

  if (!(err instanceof RequestError)) {
    res.status(500).json({ domainCode: DomainCode.UNKNOWN_ERROR, message: 'Internal Server Error' });
    return;
  }

  const requestError = err as RequestError;
  res.status(requestError.statusCode || 500).json({
    domainCode: requestError.domainCode || DomainCode.UNKNOWN_ERROR,
    message: err.message || 'Internal Server Error',
    error: err.error,
  });
};

export default errorHandler;
