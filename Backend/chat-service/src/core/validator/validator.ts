import { Request, Response, NextFunction } from 'express';
import { ContextRunner, validationResult } from 'express-validator';
import { BadRequestError } from '../../core/responses/ErrorResponse';
import { DomainCode } from '../responses/DomainCode';

// can be reused by many routes
const validate = (validations: ContextRunner[]) => {
  return async (req: Request, _res: Response, next: NextFunction) => {
    // sequential processing, stops running validations chain if one fails.
    for (const validation of validations) {
      const result = await validation.run(req);
      if (!result.isEmpty()) {
        throw new BadRequestError(DomainCode.INVALID_INPUT_FIELD, 'Validation failed', result.array());
      }
    }

    next();
  };
};

const handleValidationErrors = (req: Request, _res: Response, next: NextFunction) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw new BadRequestError(DomainCode.INVALID_INPUT_FIELD, 'Validation failed', errors.array());
  }
  next();
};

export { validate, handleValidationErrors };