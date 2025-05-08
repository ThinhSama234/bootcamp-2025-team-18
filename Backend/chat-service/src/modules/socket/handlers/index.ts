import { Server, Socket } from "socket.io";
import logger from "../../../core/logger";
import { AddFriendToGroupPayload, JoinGroupPayload, LeaveGroupPayload, RequestSuggestionsPayload, SendImageMessagePayload, SendTextMessagePayload, SocketClientEvent } from "../types/socketClient.types";
import { SocketServerEvent } from "../types/socketServer.types";
import { handleSendImageMessage, handleSendTextMessage } from "./message.handler";
import { handleRequestSuggestions } from "./suggestion.handler";
import { handleUserJoinGroup, handleUserLeaveGroup } from "./groupAccess.handler";
import { RequestError } from "../../../core/responses/ErrorResponse";


const wrapHandler = (handler: Function) => {
  return async (io: Server, socket: Socket, payload: any) => {
    try {
      await handler(io, socket, payload);
    } 
    catch (error) {
      logger.error(`Socket handler error: ${error}`);
      if (error instanceof RequestError) {
        socket.emit(SocketServerEvent.ERROR, {
          domainCode: error.domainCode,
          message: error.message
        });
      }
      else {
        socket.emit(SocketServerEvent.ERROR, {
          message: 'An error occurred while processing your request'
        });
      }
    }
  };
};

export default function registerHandlers(io: Server, socket: Socket): void {
  socket.on(SocketClientEvent.JOIN_GROUP, (payload: JoinGroupPayload) => wrapHandler(handleUserJoinGroup)(io, socket, payload));
  socket.on(SocketClientEvent.LEAVE_GROUP, (payload: LeaveGroupPayload) => wrapHandler(handleUserLeaveGroup)(io, socket, payload));
  socket.on(SocketClientEvent.ADD_FRIEND_TO_GROUP, (payload: AddFriendToGroupPayload) => wrapHandler(handleUserJoinGroup)(io, socket, payload));

  socket.on(SocketClientEvent.SEND_TEXT_MESSAGE, (payload: SendTextMessagePayload) => wrapHandler(handleSendTextMessage)(io, socket, payload));
  socket.on(SocketClientEvent.SEND_IMAGE_MESSAGE, (payload: SendImageMessagePayload) => wrapHandler(handleSendImageMessage)(io, socket, payload));

  socket.on(SocketClientEvent.REQUEST_SUGGESTIONS, (payload: RequestSuggestionsPayload) => wrapHandler(handleRequestSuggestions)(io, socket, payload));
}