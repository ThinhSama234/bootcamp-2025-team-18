import express from 'express';
import { OKResponse } from '../core/responses/SuccessResponse';
import messageRouter from './message.route';
import groupRouter from './group.route';

const router = express.Router();

router.get('/', (_req, res) => {
  new OKResponse({ message: '😊 Chat Service is running successfully!' }).send(res);
});

router.use('/api/v1/messages', messageRouter);
router.use('/api/v1/groups', groupRouter);


export default router;