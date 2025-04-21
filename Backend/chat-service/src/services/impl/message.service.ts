import { DomainCode } from "../../core/responses/DomainCode";
import { NotFoundError } from "../../core/responses/ErrorResponse";
import { IMessageService } from "../message.service";
import Message from "../../models/message.model";
import { IMessage, MessageFactory, MessageQuery, MessageType } from "../../types/message.types";

const DEFAULT_LIMIT_MESSAGES = 20;

export class MessageService implements IMessageService {
  async createMessage(messageData: Omit<IMessage, "id" | "createdAt" | "updatedAt">): Promise<IMessage> {
    const messageDoc = await new Message(messageData).save();

    return this.toMessage(messageDoc);
  }

  async getMessagesByGroupName(query: MessageQuery): Promise<IMessage[]> {
    const { groupName, senderUsername, beforeId, limit = DEFAULT_LIMIT_MESSAGES, messageType } = query;

    const filter: any = { groupName };

    if (senderUsername) filter.senderUsername = senderUsername;
    if (beforeId) filter._id = { $lt: beforeId };
    if (messageType) filter.messageType = messageType;

    const messages = await Message.find(filter)
      .sort({ createdAt: -1 })
      .limit(limit);

    return messages.map(message => this.toMessage(message));
  }

  async updateTextMessageContent(messageId: string, content: string): Promise<IMessage> {
    let message = await Message.findById(messageId);
    if (!message) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Message not found");
    }
    if (message.messageType != MessageType.TEXT) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Message is not a text message");
    }

    message = await Message.findByIdAndUpdate(
      messageId,
      { content },
      { new: true }
    );

    return this.toMessage(message);
  }

  async deleteMessage(messageId: string): Promise<void> {
    const message = await Message.findByIdAndDelete(messageId);
    if (!message) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Message not found");
    }
  }

  private toMessage(doc: any): IMessage {
    return MessageFactory.createMessage(doc);
  }

}

export default new MessageService();