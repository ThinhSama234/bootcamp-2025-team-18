import { Server, Socket } from "socket.io";
import { SendMessagePayload } from "../types/socketClient.types";
import messageService from "../../../services/impl/message.service";
import { TextMessage } from "../../../types/message.types";
import groupService from "../../../services/impl/group.service";
import logger from "../../../core/logger";
import { SocketServerEvent } from "../types/socketServer.types";



export async function handleSendTextMessage(io: Server, socket: Socket, payload: SendMessagePayload): Promise<void> {
  const { groupName, content } = payload;
  const senderUsername = socket.handshake.auth.username;
  
  const message = await messageService.createMessage(new TextMessage("", senderUsername, groupName, content));
  await groupService.updateLastMessage(groupName, message.content, message.createdAt!);
  
  io.to(groupName).emit(SocketServerEvent.RECEIVE_MESSAGE, message);

  logger.info(`Message sent in group ${groupName} by ${senderUsername}`);
}

