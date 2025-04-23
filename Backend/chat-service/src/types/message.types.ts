
export enum MessageType {
  TEXT = "text",
  IMAGE = "image",
  FILE = "file",
  SUGGESTIONS = "suggestions",
}

export abstract class IMessage {
  id: string;
  messageType: MessageType;
  senderUsername: string;
  groupName: string;
  createdAt?: Date;
  updatedAt?: Date;

  constructor(
    id: string,
    messageType: MessageType,
    senderUsername: string,
    groupName: string,
    createdAt?: Date,
    updatedAt?: Date
  ) {
    this.id = id;
    this.messageType = messageType;
    this.senderUsername = senderUsername;
    this.groupName = groupName;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }

  abstract get content(): any;
}

export class TextMessage extends IMessage {
  messageContent: string;

  constructor(id: string, senderUsername: string, groupName: string, messageContent: string, createdAt?: Date, updatedAt?: Date) {
    super(id, MessageType.TEXT, senderUsername, groupName, createdAt, updatedAt);
    this.messageContent = messageContent;
  }

  get content(): any {
    return this.messageContent;
  }
}

export class SuggestionMessage extends IMessage {
  suggestionId?: string;
  suggestions?: string[];

  constructor(id: string, senderUsername: string, groupName: string, suggestionId: string, suggestions: string[], createdAt?: Date, updatedAt?: Date) {
    super(id, MessageType.SUGGESTIONS, senderUsername, groupName, createdAt, updatedAt);
     this.suggestionId = suggestionId;
    this.suggestions = suggestions;
  }

  get content(): any {
    return { 
      suggestionId: this.suggestionId,
      suggestions: this.suggestions,
    }
  }
}

export class MessageFactory {
  static createMessage(doc: any): IMessage {
    switch (doc.messageType) {
      case MessageType.TEXT:
        return new TextMessage(
          doc._id.toString(),
          doc.senderUsername,
          doc.groupName,
          doc.content,
          doc.createdAt,
          doc.updatedAt
        );
      case MessageType.SUGGESTIONS:
        return new SuggestionMessage(
          doc._id.toString(),
          doc.senderUsername,
          doc.groupName,
          doc.content.suggestionId,
          doc.content.suggestions,
          doc.createdAt,
          doc.updatedAt
        );
      default:
        throw new Error("Unknown message type");
    }
  }
}

export interface MessageQuery {
  groupName: string;
  beforeId?: string;
  limit?: number;
  messageType?: string;
}