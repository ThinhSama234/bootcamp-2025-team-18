import express from 'express';
import { OKResponse } from '../core/responses/SuccessResponse';
import messageRouter from './message.route';

const router = express.Router();

router.get('/', (_req, res) => {
  new OKResponse({ message: '😊 Chat Service is running successfully!' }).send(res);
});

router.use('/messages', messageRouter);

export default router;