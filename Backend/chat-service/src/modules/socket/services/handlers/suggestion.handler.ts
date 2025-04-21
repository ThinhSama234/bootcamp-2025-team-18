import { Server } from "http";
import { Socket } from "socket.io";
import { SocketServerEvent } from "../../types/socketServer.types";
import { RequestSuggestionsPayload } from "../../types/socketClient.types";


export async function handleRequestSuggestions(io: Server, socket: Socket, payload: RequestSuggestionsPayload): Promise<void> {
  const { k, messages } = payload;
  if (k <= 0) {
    socket.emit(SocketServerEvent.ERROR, { message: 'Invalid value for k' });
    return;
  }

  
}