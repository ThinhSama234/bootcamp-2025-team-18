import { Server, Socket } from "socket.io";
import { SendMessagePayload, SocketClientEvent } from "../../types/socketClient.types";
import { handleSendTextMessage } from "./message.handler";
import { SocketServerEvent } from "../../types/socketServer.types";
import logger from "../../../../core/logger";


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
  socket.on(SocketClientEvent.SEND_MESSAGE, (payload: SendMessagePayload) =>  wrapHandler(handleSendTextMessage)(io, socket, payload));
  
}