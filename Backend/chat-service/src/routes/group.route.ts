import express from 'express';
import { validate } from '../core/validator/validator';
import groupController from '../controllers/group.controller';
import { validateCreateGroup, validateGetGroupsByUsername } from './validators/group.validator';

const router = express.Router();

router.post(
  '/',
  validate(validateCreateGroup),
  groupController.createGroup.bind(groupController)
)

router.get(
  '/:username',
  validate(validateGetGroupsByUsername),
  groupController.getGroupsByUsername.bind(groupController)
)

export default router;