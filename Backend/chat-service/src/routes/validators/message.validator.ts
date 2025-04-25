import { body, param, query } from 'express-validator';
import { MessageTypes } from '../../models/message.model';

export const validateCreateMessage = [
  body('senderUsername')
    .trim()
    .notEmpty().withMessage('Sender username is required')
    .isString().withMessage('Sender username must be a string'),
  body('groupName')
    .trim()
    .notEmpty().withMessage('Group name is required')
    .isString().withMessage('Group name must be a string'),
  body('messageType')
    .trim()
    .notEmpty().withMessage('Message type is required')
    .isIn(MessageTypes).withMessage(`Message type must be one of: ${MessageTypes.join(', ')}`),
  body('content')
    .trim()
    .notEmpty().withMessage('Content is required')
    .isString().withMessage('Content must be a string')
];

export const validateGetMessages = [
  param('groupName')
    .trim()
    .notEmpty().withMessage('Group name is required')
    .isString().withMessage('Group name must be a string'),
  query('beforeId')
    .optional()
    .trim()
    .isMongoId().withMessage('Invalid message ID format'),
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100')
    .toInt(),
  query('messageType')
    .optional()
    .trim()
    .isIn(MessageTypes).withMessage(`Message type must be one of: ${MessageTypes.join(', ')}`)
];

export const validateGetUserGroups = [
  param('username')
    .trim()
    .notEmpty().withMessage('Username is required')
    .isString().withMessage('Username must be a string')
];

export const validateUpdateMessage = [
  param('messageId')
    .trim()
    .notEmpty().withMessage('Message ID is required')
    .isMongoId().withMessage('Invalid message ID format'),
  body('content')
    .trim()
    .notEmpty().withMessage('Content is required')
    .isString().withMessage('Content must be a string')
];

export const validateDeleteMessage = [
  param('messageId')
    .trim()
    .notEmpty().withMessage('Message ID is required')
    .isMongoId().withMessage('Invalid message ID format')
];