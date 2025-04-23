import { Server, Socket } from 'socket.io';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import logger from '../../core/logger';
import { SocketServerEvent } from './types/socketServer.types';
import registerHandlers from './handlers';
import groupService from '../../services/impl/group.service';

export class SocketService {
  private io: Server<DefaultEventsMap, DefaultEventsMap, DefaultEventsMap, any>;
  private socketToUsername: Map<string, string> = new Map(); // socket.id -> username
  
  constructor(io: Server) {
    this.io = io;
    this.setupSocketHandlers();
  }

  private setupSocketHandlers(): void {
    this.io.engine.on("connection_error", (err) => {
      logger.error(`Connection error: ${err.message}`);
    });

    this.io.use(async (socket: Socket, next: any) => {
      try {
        const username = socket.handshake.auth.username;
        if (!username) {
          return next(new Error('Username is required'));
        }
        this.socketToUsername.set(socket.id, username);
        
        next();
      } catch (error) {
        logger.error(`Authentication error: ${error}`);
        next(new Error('Authentication failed'));
      }
    });

    this.io.on('connection', async (socket: Socket) => {
      socket.on('error', (error) => {
        logger.error(`Socket error for ${socket.id}: ${error.message}`);
        socket.emit(SocketServerEvent.ERROR, { message: 'Internal server error' });
      });

      socket.on('connect_error', (error) => {
        logger.error(`Connection error for ${socket.id}: ${error.message}`);
      });

      try {
        const username = this.socketToUsername.get(socket.id)!;
        
        logger.info(`Client connected: ${socket.id} (${username})`);
        
        const userGroups = (await groupService.getGroupsByUsername(username)).map((group) => group.groupName);

        for (const groupName of userGroups) {
          await socket.join(groupName);
        }

        socket.on('disconnect', () => this.handleDisconnect(socket));

        registerHandlers(this.io, socket);
      } 
      catch (error) {
        logger.error(`Error in connection handler: ${error}`);
        socket.emit(SocketServerEvent.ERROR, { message: 'Failed to initialize connection' });
      }
    });
  }

  private handleDisconnect(socket: Socket): void {
    const username = this.socketToUsername.get(socket.id);
    logger.info(`Client disconnected: ${socket.id} (${username})`);
    
    if (username) {
      this.socketToUsername.delete(socket.id);
    }
  }
}