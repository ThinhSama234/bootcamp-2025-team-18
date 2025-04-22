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
  data?: any;
};

class SuccessResponse {
  statusCode: number;
  domainCode: DomainCode;
  message: string;
  data?: any;

  constructor({
    statusCode = SuccessStatusCode.OK,
    domainCode = DomainCode.SUCCESS,
    message = SuccessMessage.OK,
    data,
  }: SuccessObject) {
    this.statusCode = statusCode;
    this.domainCode = domainCode;
    this.message = message;
    this.data = data;
  }

  send(res: Response) {
    res.status(this.statusCode).json({
      domainCode: this.domainCode,
      message: this.message,
      data: this.data,
    });
  }
}

class OKResponse extends SuccessResponse {
  constructor({ message, data }: { message?: string; data?: any }) {
    super({
      statusCode: SuccessStatusCode.OK,
      message: message || SuccessMessage.OK,
      data,
    });
  }
}

class CreatedResponse extends SuccessResponse {
  constructor({ message, data }: { message?: string; data?: any }) {
    super({
      statusCode: SuccessStatusCode.CREATED,
      message: message || SuccessMessage.CREATED,
      data,
    });
  }
}

class AcceptedResponse extends SuccessResponse {
  constructor({ message, data }: { message?: string; data?: any }) {
    super({
      statusCode: SuccessStatusCode.ACCEPTED,
      message: message || SuccessMessage.ACCEPTED,
      data,
    });
  }
}

class NoContentResponse extends SuccessResponse {
  constructor({ message, data }: { message?: string; data?: any }) {
    super({
      statusCode: SuccessStatusCode.NO_CONTENT,
      message: message || SuccessMessage.NO_CONTENT,
      data,
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
