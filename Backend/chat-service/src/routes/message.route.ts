import express from 'express';
import { validate } from '../core/validator/validator';
import {
  validateCreateMessage,
  validateGetMessages,
  validateGetUserGroups,
  validateUpdateMessage,
  validateDeleteMessage,
} from '../validators/message.validator';
import messageController from '../controllers/message.controller';

const router = express.Router();

// Message CRUD operations
router.post(
  '/',
  validate(validateCreateMessage),
  messageController.createMessage.bind(messageController)
);

router.get(
  '/',
  validate(validateGetMessages),
  messageController.getMessages.bind(messageController)
);

router.patch(
  '/:messageId',
  validate(validateUpdateMessage),
  messageController.updateMessage.bind(messageController)
);

router.delete(
  '/:messageId',
  validate(validateDeleteMessage),
  messageController.deleteMessage.bind(messageController)
);

// Group operations
router.get(
  '/groups/:username',
  validate(validateGetUserGroups),
  messageController.getUserGroups.bind(messageController)
);

export default router;