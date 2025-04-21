import { Server, Socket } from "socket.io";
import { ReceiveSuggestionPayload, SocketServerEvent } from "../../types/socketServer.types";
import { RequestSuggestionsPayload } from "../../types/socketClient.types";
import suggestionService from "../../../../services/impl/suggestion.service";
import messageService from "../../../../services/impl/message.service";
import { SuggestionMessage } from "../../../../types/message.types";


export async function handleRequestSuggestions(io: Server, socket: Socket, payload: RequestSuggestionsPayload): Promise<void> {
  const { groupName, k, messages } = payload;
  if (k <= 0) {
    socket.emit(SocketServerEvent.ERROR, { message: 'Invalid value for k' });
    return;
  }

  const suggestionId = await suggestionService.initSuggestionRequest(k, messages);
  
  await messageService.createMessage(new SuggestionMessage("", "suggestion_service", groupName, suggestionId, []));
  
  for (let i = 0; i < k; i++) {
    const suggestion = await suggestionService.getSingleSuggestion(suggestionId);

    await messageService.addSuggestionToMessage(suggestionId, suggestion);

    const singleSuggestion: ReceiveSuggestionPayload = {
      suggestionId,
      suggestion,
      timestamp: new Date(),
    }
    io.to(groupName).emit(SocketServerEvent.RECEIVE_SUGGESTION, singleSuggestion);
  }
}