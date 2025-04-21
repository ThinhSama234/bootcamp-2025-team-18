import { Server, Socket } from 'socket.io';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import logger from '../../../core/logger';
import { JoinGroupPayload, LeaveGroupPayload, SocketClientEvent } from '../types/socketClient.types';
import { SocketServerEvent, UserJoinedPayload, UserLeftPayload } from '../types/socketServer.types';
import registerHandlers from './handlers';
import groupService from '../../../services/impl/group.service';

export class SocketService {
  private io: Server<DefaultEventsMap, DefaultEventsMap, DefaultEventsMap, any>;
  private socketToUsername: Map<string, string> = new Map(); // socket.id -> username
  private userSockets: Map<string, Set<string>> = new Map(); // username -> Set of socket IDs
  
  constructor(io: Server) {
    this.io = io;
    this.setupSocketHandlers();
  }

  private setupSocketHandlers(): void {
    this.io.use(async (socket, next) => {
      try {
        const username = socket.handshake.auth.username;
        if (!username) {
          return next(new Error('Username is required'));
        }

        this.socketToUsername.set(socket.id, username);
        
        if (!this.userSockets.has(username)) {
          this.userSockets.set(username, new Set());
        }
        this.userSockets.get(username)!.add(socket.id);
        
        next();
      } catch (error) {
        next(new Error('Authentication failed'));
      }
    });

    this.io.on('connection', async (socket: Socket) => {
      const username = this.socketToUsername.get(socket.id)!;
      
      logger.info(`Client connected: ${socket.id} (${username})`);
      
      const userGroups = (await groupService.getGroupsByUsername(username)).map((group) => group.groupName);

      for (const groupName of userGroups) {
        await socket.join(groupName);
      }

      socket.on(SocketClientEvent.JOIN_GROUP, (payload: JoinGroupPayload) => this.handleJoinGroup(socket, payload));
      socket.on(SocketClientEvent.LEAVE_GROUP, (payload: LeaveGroupPayload) => this.handleLeaveGroup(socket, payload));
      socket.on('disconnect', () => this.handleDisconnect(socket));
  
      registerHandlers(this.io, socket);
    });
  }

  private async handleJoinGroup(socket: Socket, payload: JoinGroupPayload): Promise<void> {
    try {
      const { username, groupName } = payload;
      await groupService.addUserToGroup(groupName, username);
      
      await socket.join(groupName);
      const userJoinedPayload: UserJoinedPayload = {
        username,
        groupName,
        timestamp: new Date()
      }
      this.io.to(groupName).emit(SocketServerEvent.USER_JOINED, userJoinedPayload);

      logger.info(`User ${username} joined group ${groupName}`);

    } catch (error) {
      logger.error(`Error in handleJoinGroup: ${error}`);
      socket.emit(SocketServerEvent.ERROR, { message: 'Failed to join group' });
    }
  }

  private async handleLeaveGroup(socket: Socket, payload: LeaveGroupPayload): Promise<void> {
    try {
      const { username, groupName } = payload;
      await groupService.removeUserFromGroup(groupName, username);
      
      await socket.leave(groupName);

      const userLeftPayload: UserLeftPayload = {
        username,
        groupName,
        timestamp: new Date()
      }
      this.io.to(groupName).emit(SocketServerEvent.USER_LEFT, userLeftPayload);

      logger.info(`User ${username} left group ${groupName}`);
    } catch (error) {
      logger.error(`Error in handleLeaveGroup: ${error}`);
      socket.emit(SocketServerEvent.ERROR, { message: 'Failed to leave group' });
    }
  }

  private handleDisconnect(socket: Socket): void {
    const username = this.socketToUsername.get(socket.id);
    logger.info(`Client disconnected: ${socket.id} (${username})`);
    
    if (username) {
      const userSockets = this.userSockets.get(username);
      if (userSockets) {
        userSockets.delete(socket.id);
        if (userSockets.size === 0) {
          this.userSockets.delete(username);
        }
      }

      this.socketToUsername.delete(socket.id);
    }
  }
}