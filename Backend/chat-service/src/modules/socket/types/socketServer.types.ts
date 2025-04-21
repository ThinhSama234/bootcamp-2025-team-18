export enum SocketServerEvent {
  ERROR = 'error',
    
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  
  RECEIVE_MESSAGE = 'receive_message',
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

