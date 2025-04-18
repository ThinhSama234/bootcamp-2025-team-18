import { Response } from 'express';
import { DomainCode } from './DomainCode';

const SuccessStatusCode = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
};

const SuccessMessage = {
  OK: 'OK',
  CREATED: 'Created',
  ACCEPTED: 'Accepted',
  NO_CONTENT: 'No Content',
};

type SuccessObject = {
  statusCode: number;
  domainCode?: DomainCode;
  message: string;
  metadata?: any;
};

class SuccessResponse {
  statusCode: number;
  domainCode: DomainCode;
  message: string;
  metadata?: any;

  constructor({
    statusCode = SuccessStatusCode.OK,
    domainCode = DomainCode.SUCCESS,
    message = SuccessMessage.OK,
    metadata,
  }: SuccessObject) {
    this.statusCode = statusCode;
    this.domainCode = domainCode;
    this.message = message;
    this.metadata = metadata;
  }

  send(res: Response) {
    res.status(this.statusCode).json({
      domainCode: this.domainCode,
      message: this.message,
      metadata: this.metadata,
    });
  }
}

class OKResponse extends SuccessResponse {
  constructor({ message, metadata }: { message?: string; metadata?: any }) {
    super({
      statusCode: SuccessStatusCode.OK,
      message: message || SuccessMessage.OK,
      metadata,
    });
  }
}

class CreatedResponse extends SuccessResponse {
  constructor({ message, metadata }: { message?: string; metadata?: any }) {
    super({
      statusCode: SuccessStatusCode.CREATED,
      message: message || SuccessMessage.CREATED,
      metadata,
    });
  }
}

class AcceptedResponse extends SuccessResponse {
  constructor({ message, metadata }: { message?: string; metadata?: any }) {
    super({
      statusCode: SuccessStatusCode.ACCEPTED,
      message: message || SuccessMessage.ACCEPTED,
      metadata,
    });
  }
}

class NoContentResponse extends SuccessResponse {
  constructor({ message, metadata }: { message?: string; metadata?: any }) {
    super({
      statusCode: SuccessStatusCode.NO_CONTENT,
      message: message || SuccessMessage.NO_CONTENT,
      metadata,
    });
  }
}

export {
  SuccessResponse,
  OKResponse,
  CreatedResponse,
  AcceptedResponse,
  NoContentResponse,
};
