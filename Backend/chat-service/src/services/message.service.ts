import { Message, MessageQuery } from "../types/message.types";

export interface IMessageService {
  createMessage(messageData: Omit<Message, "id" | "createdAt" | "updatedAt">): Promise<Message>;
  getMessagesByGroupName(query: MessageQuery): Promise<Message[]>;
  getAllGroupsByUsernameOrderByLastMessageCreationTime(username: string): Promise<string[]>;
  updateMessageContent(messageId: string, content: string): Promise<Message>;
  deleteMessage(messageId: string): Promise<void>;
}