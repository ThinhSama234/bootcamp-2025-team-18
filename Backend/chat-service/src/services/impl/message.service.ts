import { DomainCode } from "../../core/responses/DomainCode";
import { NotFoundError } from "../../core/responses/ErrorResponse";
import { IMessageService } from "../message.service";
import Message from "../../models/message.model";
import { Message as MessageType, MessageQuery } from "../../types/message.types";

const DEFAULT_LIMIT_MESSAGES = 20;

export class MessageService implements IMessageService {
  async createMessage(messageData: Omit<MessageType, "id" | "createdAt" | "updatedAt">): Promise<MessageType> {
    const message = await new Message(messageData).save();
    return this.toMessage(message);
  }

  async getAllGroupsByUsernameOrderByLastMessageCreationTime(username: string): Promise<string[]> {
    const groups = await Message.aggregate([
      { $match: { senderUsername: username } },
      { $sort: { createdAt: -1 } },
      { $group: { _id: "$groupName", latestMessage: { $first: "$createdAt" } } },
      { $sort: { latestMessage: -1 } },
      { $project: { groupName: "$_id", _id: 0 } }
    ]);
    return groups.map(g => g.groupName);
  }

  async getMessagesByGroupName(query: MessageQuery): Promise<MessageType[]> {
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

  async updateMessageContent(messageId: string, content: string): Promise<MessageType> {
    const message = await Message.findByIdAndUpdate(
      messageId,
      { content },
      { new: true }
    );
    
    if (!message) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Message not found");
    }

    return this.toMessage(message);
  }

  async deleteMessage(messageId: string): Promise<void> {
    const message = await Message.findByIdAndDelete(messageId);
    if (!message) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Message not found");
    }
  }

  private toMessage(doc: any): MessageType {
    return {
      id: doc._id.toString(),
      senderUsername: doc.senderUsername,
      groupName: doc.groupName,
      messageType: doc.messageType,
      content: doc.content,
      createdAt: doc.createdAt,
      updatedAt: doc.updatedAt
    };
  }
}

export default new MessageService();