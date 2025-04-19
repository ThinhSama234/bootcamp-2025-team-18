export interface Message {
  id: string;
  senderUsername: string;
  groupName: string;
  messageType: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface MessageQuery {
  groupName: string;
  senderUsername?: string;
  beforeId?: string;
  limit?: number;
  messageType?: string;
}