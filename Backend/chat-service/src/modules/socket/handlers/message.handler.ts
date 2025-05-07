import { Server, Socket } from "socket.io";
import { SendImageMessagePayload, SendTextMessagePayload } from "../types/socketClient.types";
import messageService from "../../../services/impl/message.service";
import { ImageMessage, TextMessage } from "../../../types/message.types";
import logger from "../../../core/logger";
import { SocketServerEvent } from "../types/socketServer.types";
import imageService from "../../../services/impl/image.service";

export async function handleSendTextMessage(io: Server, socket: Socket, payload: SendTextMessagePayload): Promise<void> {
  const { groupName, content } = payload;
  const senderUsername = socket.handshake.auth.username;
  
  const message = await messageService.createMessage(new TextMessage("", senderUsername, groupName, content));
  
  io.to(groupName).emit(SocketServerEvent.RECEIVE_MESSAGE, message);

  logger.info(`Message sent in group ${groupName} by ${senderUsername}`);
}

export async function handleSendImageMessage(io: Server, socket: Socket, payload: SendImageMessagePayload): Promise<void> {
  const { groupName, filename, base64EncodedImage } = payload;
  const senderUsername = socket.handshake.auth.username;

  const {mimeType, buffer} = imageService.decodeBase64Image(base64EncodedImage);
  const { key, imageUrl } = await imageService.uploadImage(filename, buffer, mimeType);
  
  const message = await messageService.createMessage(new ImageMessage("", senderUsername, groupName, key, imageUrl));
  
  io.to(groupName).emit(SocketServerEvent.RECEIVE_MESSAGE, message);

  logger.info(`Image message sent in group ${groupName} by ${senderUsername}`);
}
