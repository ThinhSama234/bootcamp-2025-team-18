export enum SocketEvent {
  INITIALIZE_USER = 'initialize_user',
  JOIN_GROUP = 'join_group',
  LEAVE_GROUP = 'leave_group',
  SEND_MESSAGE = 'send_message',
  RECEIVE_MESSAGE = 'receive_message',
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  ERROR = 'error'
}

export interface JoinGroupPayload {
  username: string;
  groupName: string;
}

export interface SendMessagePayload {
  senderUsername: string;
  groupName: string;
  content: string;
  messageType: string;
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

export interface InitializeUserPayload {
  username: string;
}