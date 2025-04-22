import { body, param } from "express-validator"


export const validateCreateGroup = [
  body('groupName')
    .isString()
    .notEmpty().withMessage('Group name is required')
    .isLength({ min: 3, max: 50 }).withMessage('Group name must be between 3 and 50 characters')
    .matches(/^[a-zA-Z0-9_]+$/).withMessage('Group name can only contain letters, numbers, and underscores'),
  body('creator')
    .isString()
    .notEmpty().withMessage('Creator username is required')
    .isLength({ min: 3, max: 20 }).withMessage('Creator username must be between 3 and 20 characters')
    .matches(/^[a-zA-Z0-9_]+$/).withMessage('Creator username can only contain letters, numbers, and underscores'),
]

export const validateGetGroupsByUsername = [
  param('username')
    .isString()
    .notEmpty().withMessage('Username is required')
    .isLength({ min: 3, max: 20 }).withMessage('Username must be between 3 and 20 characters')
    .matches(/^[a-zA-Z0-9_]+$/).withMessage('Username can only contain letters, numbers, and underscores'),
]