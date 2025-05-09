import { Server, Socket } from "socket.io";
import { ReceiveSuggestionIDPayload, ReceiveSuggestionPayload, SocketServerEvent } from "../types/socketServer.types";
import { RequestSuggestionsPayload } from "../types/socketClient.types";
import suggestionService from "../../../services/impl/suggestion.service";
import messageService from "../../../services/impl/message.service";
import { SuggestionMessage } from "../../../types/message.types";
import logger from "../../../core/logger";


export async function handleRequestSuggestions(io: Server, socket: Socket, payload: RequestSuggestionsPayload): Promise<void> {
  const { groupName, k, messages, image_urls, coordinates } = payload;
  if (k <= 0) {
    socket.emit(SocketServerEvent.ERROR, { message: 'Invalid value for k' });
    return;
  }

  suggestionService.getSuggestions(
    k, messages, image_urls, coordinates,
    async (suggestionId: string) => {
      const suggestionIdPayload: ReceiveSuggestionIDPayload = {
        suggestionId: suggestionId,
      }
      await messageService.createMessage(new SuggestionMessage("", "suggestion_service", groupName, messages, image_urls, coordinates, suggestionId, []));
      
      socket.emit(SocketServerEvent.RECEIVE_SUGGESTION_ID, suggestionIdPayload);
    }, 
    async (suggestionId: string, suggestion: string) => {
      await messageService.addSuggestionToMessage(suggestionId, suggestion);
  
      const singleSuggestion: ReceiveSuggestionPayload = {
        suggestionId,
        suggestion,
        timestamp: new Date(),
      }
      io.to(groupName).emit(SocketServerEvent.RECEIVE_SUGGESTION, singleSuggestion);
    }, 
    (error: any) => {
      socket.emit(SocketServerEvent.ERROR, { message: error.message });
      logger.error(`Error in suggestion service: ${error.message}`);
    }
  )
}