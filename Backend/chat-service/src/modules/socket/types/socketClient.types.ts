export enum SocketClientEvent {
  JOIN_GROUP = 'join_group',
  LEAVE_GROUP = 'leave_group',

  SEND_MESSAGE = 'send_text_message',
  
  REQUEST_SUGGESTIONS = 'request_suggestions',
}


export interface JoinGroupPayload {
  groupName: string;
}

export interface LeaveGroupPayload {
  groupName: string;
}

export interface SendTextMessagePayload {
  groupName: string;
  content: string;
}

export interface RequestSuggestionsPayload {
  groupName: string;
  k: number;
  messages: string[];
} 

