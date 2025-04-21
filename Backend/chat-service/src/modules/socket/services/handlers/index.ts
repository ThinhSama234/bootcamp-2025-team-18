import { Server, Socket } from "socket.io";
import { SendMessagePayload, SocketClientEvent } from "../../types/socketClient.types";
import { handleSendTextMessage } from "./message.hander";


export default function registerHandlers(io: Server, socket: Socket): void {
  socket.on(SocketClientEvent.SEND_MESSAGE, (payload: SendMessagePayload) => handleSendTextMessage(io, socket, payload));
  
}