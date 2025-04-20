import { Server, Socket } from 'socket.io';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import logger from '../../../core/logger';
import { JoinGroupPayload, SendMessagePayload, SocketEvent } from '../types/socket.types';
import messageService from '../../../services/impl/message.service';

export class SocketService {
  private io: Server<DefaultEventsMap, DefaultEventsMap, DefaultEventsMap, any>;
  private userSockets: Map<string, Set<string>> = new Map(); // username -> Set of socket IDs
  private groupUsers: Map<string, Set<string>> = new Map(); // groupName -> Set of usernames
  private socketToUsername: Map<string, string> = new Map(); // socket.id -> username

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

        const userGroups = await messageService.getAllGroupsByUsernameOrderByLastMessageCreationTime(username);
        
        if (!this.userSockets.has(username)) {
          this.userSockets.set(username, new Set());
        }
        this.userSockets.get(username)!.add(socket.id);

        (socket as any).userGroups = userGroups;
        
        next();
      } catch (error) {
        next(new Error('Authentication failed'));
      }
    });

    this.io.on('connection', (socket: Socket) => {
      const username = this.socketToUsername.get(socket.id);
      const userGroups = (socket as any).userGroups as string[];
      
      logger.info(`Client connected: ${socket.id} (${username})`);

      for (const groupName of userGroups) {
        this.joinGroup(socket, { username: username!, groupName });
      }

      socket.on(SocketEvent.JOIN_GROUP, (payload: JoinGroupPayload) => this.handleJoinGroup(socket, payload));
      socket.on(SocketEvent.LEAVE_GROUP, (payload: JoinGroupPayload) => this.handleLeaveGroup(socket, payload));
      socket.on(SocketEvent.SEND_MESSAGE, (payload: SendMessagePayload) => this.handleSendMessage(socket, payload));
      socket.on('disconnect', () => this.handleDisconnect(socket));
    });
  }

  private async joinGroup(socket: Socket, payload: JoinGroupPayload): Promise<void> {
    const { username, groupName } = payload;

    await socket.join(groupName);

    if (!this.groupUsers.has(groupName)) {
      this.groupUsers.set(groupName, new Set());
    }
    this.groupUsers.get(groupName)!.add(username);

    this.io.to(groupName).emit(SocketEvent.USER_JOINED, {
      username,
      groupName,
      timestamp: new Date()
    });

    logger.info(`User ${username} joined group ${groupName}`);
  }

  private async handleJoinGroup(socket: Socket, payload: JoinGroupPayload): Promise<void> {
    try {
      await this.joinGroup(socket, payload);
    } catch (error) {
      logger.error(`Error in handleJoinGroup: ${error}`);
      socket.emit(SocketEvent.ERROR, { message: 'Failed to join group' });
    }
  }

  private async handleLeaveGroup(socket: Socket, payload: JoinGroupPayload): Promise<void> {
    try {
      const { username, groupName } = payload;

      await socket.leave(groupName);
      
      this.groupUsers.get(groupName)?.delete(username);
      if (this.groupUsers.get(groupName)?.size === 0) {
        this.groupUsers.delete(groupName);
      }

      this.io.to(groupName).emit(SocketEvent.USER_LEFT, {
        username,
        groupName,
        timestamp: new Date()
      });

      logger.info(`User ${username} left group ${groupName}`);
    } catch (error) {
      logger.error(`Error in handleLeaveGroup: ${error}`);
      socket.emit(SocketEvent.ERROR, { message: 'Failed to leave group' });
    }
  }

  private async handleSendMessage(socket: Socket, payload: SendMessagePayload): Promise<void> {
    try {
      const { senderUsername, groupName, content, messageType } = payload;

      const message = await messageService.createMessage({
        senderUsername,
        groupName,
        content,
        messageType
      });

      this.io.to(groupName).emit(SocketEvent.RECEIVE_MESSAGE, message);

      logger.info(`Message sent in group ${groupName} by ${senderUsername}`);
    } catch (error) {
      logger.error(`Error in handleSendMessage: ${error}`);
      socket.emit(SocketEvent.ERROR, { message: 'Failed to send message' });
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