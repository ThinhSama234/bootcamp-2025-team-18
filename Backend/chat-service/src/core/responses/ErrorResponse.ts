import { DomainCode } from "./DomainCode";

const enum ErrorStatusCode {
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  INTERNAL_SERVER_ERROR = 500,
}

const ErrorMessage = {
  BAD_REQUEST: 'Bad Request',
  UNAUTHORIZED: 'Unauthorized',
  FORBIDDEN: 'Forbidden',
  NOT_FOUND: 'Not Found',
  INTERNAL_SERVER_ERROR: 'Internal Server Error',
};

type ErrorObject = {
  statusCode: ErrorStatusCode;
  domainCode?: DomainCode;
  message: string;
  error?: any;
};

class RequestError extends Error {
  statusCode: ErrorStatusCode;
  domainCode: DomainCode;
  error: any;

  constructor({
    statusCode = ErrorStatusCode.INTERNAL_SERVER_ERROR,
    domainCode = DomainCode.UNKNOWN_ERROR,
    message = ErrorMessage.INTERNAL_SERVER_ERROR,
    error
  }: ErrorObject) {
    super(message);
    this.statusCode = statusCode;
    this.domainCode = domainCode;
    this.error = error;
  }
}

class NotFoundError extends RequestError {
  constructor(domainCode: DomainCode = DomainCode.UNKNOWN_ERROR, message: string = ErrorMessage.NOT_FOUND, error?: any) {
    super({domainCode: domainCode, statusCode: ErrorStatusCode.NOT_FOUND, message, error });
  }
}

class BadRequestError extends RequestError {
  constructor(domainCode: DomainCode = DomainCode.UNKNOWN_ERROR, message: string = ErrorMessage.BAD_REQUEST, error?: any) {
    super({domainCode: domainCode, statusCode: ErrorStatusCode.BAD_REQUEST, message, error });
  }
}

class UnauthorizedError extends RequestError {
  constructor(message: string = ErrorMessage.UNAUTHORIZED, error?: any) {
    super({ statusCode: ErrorStatusCode.UNAUTHORIZED, domainCode: DomainCode.UNAUTHORIZED, message, error });
  }
}

class ForbiddenError extends RequestError {
  constructor(message: string = ErrorMessage.FORBIDDEN, error?: any) {
    super({ statusCode: ErrorStatusCode.FORBIDDEN, domainCode: DomainCode.FORBIDDEN, message, error });
  }
}

class InternalServerError extends RequestError {
  constructor(message: string = ErrorMessage.INTERNAL_SERVER_ERROR, error?: any) {
    super({ statusCode: ErrorStatusCode.INTERNAL_SERVER_ERROR, message, error });
  }
}

export {
  RequestError,
  NotFoundError,
  BadRequestError,
  UnauthorizedError,
  ForbiddenError,
  InternalServerError,
};
