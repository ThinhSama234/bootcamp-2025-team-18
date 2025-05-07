import { Server, Socket } from "socket.io";
import logger from "../../../core/logger";
import { AddFriendToGroupPayload, JoinGroupPayload, LeaveGroupPayload, SendMessagePayload, SocketClientEvent } from "../types/socketClient.types";
import { SocketServerEvent } from "../types/socketServer.types";
import { handleSendTextMessage } from "./message.handler";
import { handleRequestSuggestions } from "./suggestion.handler";
import { handleUserJoinGroup, handleUserLeaveGroup } from "./groupAccess.handler";


const wrapHandler = (handler: Function) => {
  return async (io: Server, socket: Socket, payload: any) => {
    try {
      await handler(io, socket, payload);
    } 
    catch (error) {
      logger.error(`Socket handler error: ${error}`);
      socket.emit(SocketServerEvent.ERROR, {
        message: 'An error occurred while processing your request'
      });
    }
  };
};

export default function registerHandlers(io: Server, socket: Socket): void {
  socket.on(SocketClientEvent.JOIN_GROUP, (payload: JoinGroupPayload) => wrapHandler(handleUserJoinGroup)(io, socket, payload));
  socket.on(SocketClientEvent.LEAVE_GROUP, (payload: LeaveGroupPayload) => wrapHandler(handleUserLeaveGroup)(io, socket, payload));
  socket.on(SocketClientEvent.ADD_FRIEND_TO_GROUP, (payload: AddFriendToGroupPayload) => wrapHandler(handleUserJoinGroup)(io, socket, payload));

  socket.on(SocketClientEvent.SEND_MESSAGE, (payload: SendMessagePayload) => wrapHandler(handleSendTextMessage)(io, socket, payload));

  socket.on(SocketClientEvent.REQUEST_SUGGESTIONS, (payload: SendMessagePayload) => wrapHandler(handleRequestSuggestions)(io, socket, payload));
}