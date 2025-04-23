import { IMessage } from "../../../types/message.types";

export enum SocketServerEvent {
  ERROR = 'error',
    
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  
  RECEIVE_MESSAGE = 'receive_message',
  RECEIVE_SUGGESTION_ID = 'receive_suggestion_id',
  RECEIVE_SUGGESTION = 'receive_suggestion',
}


export interface UserJoinedPayload {
  username: string;
  groupName: string;
  timestamp: Date;
}

export interface UserLeftPayload {
  username: string;
  groupName: string;
  timestamp: Date;
}

export type ReceiveMessagePayload = IMessage;

export type ReceiveSuggestionIDPayload = {
  suggestionId: string;
}

export interface ReceiveSuggestionPayload {
  suggestionId: string;
  suggestion: string;
  timestamp: Date;
}

