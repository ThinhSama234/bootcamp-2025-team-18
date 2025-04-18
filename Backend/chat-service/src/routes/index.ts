import express from 'express';
import { OKResponse } from '../core/responses/SuccessResponse';

const router = express.Router();

router.get('/', (_req, res) => {
  new OKResponse({ message: '😊 Chat Service is running successfully!' }).send(res);
});


export default router;