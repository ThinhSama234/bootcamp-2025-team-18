export enum SocketClientEvent {
  JOIN_GROUP = 'join_group',
  LEAVE_GROUP = 'leave_group',

  SEND_MESSAGE = 'send_message',
  
  REQUEST_SUGGESTIONS = 'request_suggestions',
}


export interface JoinGroupPayload {
  username: string;
  groupName: string;
}

export interface LeaveGroupPayload {
  username: string;
  groupName: string;
}

export interface SendMessagePayload {
  senderUsername: string;
  groupName: string;
  content: string;
  messageType: string;
}

export interface RequestSuggestionsPayload {
  groupName: string;
  k: number;
  messages: string[];
} 

