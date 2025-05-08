import { Server, Socket } from "socket.io";
import { AddFriendToGroupPayload, JoinGroupPayload, LeaveGroupPayload } from "../types/socketClient.types";
import groupService from "../../../services/impl/group.service";
import { SocketServerEvent, UserJoinedPayload, UserLeftPayload } from "../types/socketServer.types";
import logger from "../../../core/logger";



export async function handleUserJoinGroup(io: Server, socket: Socket, payload: JoinGroupPayload): Promise<void> {
  const { groupName } = payload;
  const username = socket.handshake.auth.username;
  
  await groupService.addUserToGroup(groupName, username);
  
  await socket.join(groupName);
  const userJoinedPayload: UserJoinedPayload = {
    username,
    groupName,
    timestamp: new Date()
  }
  io.to(groupName).emit(SocketServerEvent.USER_JOINED, userJoinedPayload);

  logger.info(`User ${username} joined group ${groupName}`);
}

export async function handleUserLeaveGroup(io: Server, socket: Socket, payload: LeaveGroupPayload): Promise<void> {
  const { groupName } = payload;
  const username = socket.handshake.auth.username;
  await groupService.removeUserFromGroup(groupName, username);
  
  await socket.leave(groupName);

  const userLeftPayload: UserLeftPayload = {
    username,
    groupName,
    timestamp: new Date()
  }
  io.to(groupName).emit(SocketServerEvent.USER_LEFT, userLeftPayload);

  logger.info(`User ${username} left group ${groupName}`);
}

export async function handleAddFriendToGroup(io: Server, socket: Socket, payload: AddFriendToGroupPayload): Promise<void> {
  const { groupName, friendUsername } = payload;
  
  await groupService.addUserToGroup(groupName, friendUsername);
  
  const userJoinedPayload: UserJoinedPayload = {
    username: friendUsername,
    groupName,
    timestamp: new Date()
  }
  io.to(groupName).emit(SocketServerEvent.USER_JOINED, userJoinedPayload);

  logger.info(`User ${friendUsername} joined group ${groupName}`);
}
