import express from 'express';
const app = express();
import cors from 'cors';
import morgan from 'morgan';
import compression from 'compression';
import 'express-async-errors';
import dotenv from 'dotenv';
dotenv.config();

import connectDB from './database/db';
import logger from './core/logger';


// import middlewares and routes
import notFoundHandler from './core/errors/not-found-handler';
import errorHandler from './core/errors/error-handler';

import router from './routes';

// middlewares
app.use(cors());
app.use(morgan('dev'));
app.use(compression());

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// routes
app.use(router);

// error handler
app.use(notFoundHandler);
app.use(errorHandler);

// start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, async () => {
  await connectDB();

  logger.info(`Server is running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV ?? 'development'}`);
  logger.info(`Open: http://localhost:${PORT}`);
});
