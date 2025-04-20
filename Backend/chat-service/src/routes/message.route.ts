import express from 'express';
import { validate } from '../core/validator/validator';
import {
  validateGetMessages,
} from '../validators/message.validator';
import messageController from '../controllers/message.controller';

const router = express.Router();

router.get(
  '/',
  validate(validateGetMessages),
  messageController.getMessages.bind(messageController)
);

// router.get(
//   '/groups/:username',
//   validate(validateGetUserGroups),
//   messageController.getUserGroups.bind(messageController)
// );

export default router;