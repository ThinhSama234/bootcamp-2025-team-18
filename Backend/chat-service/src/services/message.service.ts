import { IMessage, MessageQuery } from "../types/message.types";

export interface IMessageService {
  createMessage(messageData: Omit<IMessage, "id" | "createdAt" | "updatedAt">): Promise<IMessage>;
  getMessagesByGroupName(query: MessageQuery): Promise<IMessage[]>;
  updateTextMessageContent(messageId: string, content: string): Promise<IMessage>;
  addSuggestionToMessage(suggestionId: string, suggestion: string): Promise<IMessage>;
  deleteMessage(messageId: string): Promise<void>;
}