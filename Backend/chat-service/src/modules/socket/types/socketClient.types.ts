export enum SocketClientEvent {
  JOIN_GROUP = 'join_group',
  LEAVE_GROUP = 'leave_group',
  ADD_FRIEND_TO_GROUP = 'add_friend_to_group',

  SEND_TEXT_MESSAGE = 'send_text_message',
  SEND_IMAGE_MESSAGE = 'send_image_message',
  
  REQUEST_SUGGESTIONS = 'request_suggestions',
}


export interface JoinGroupPayload {
  groupName: string;
}

export interface LeaveGroupPayload {
  groupName: string;
}

export interface AddFriendToGroupPayload {
  groupName: string;
  friendUsername: string;
}

export interface SendTextMessagePayload {
  groupName: string;
  content: string;
}

export interface SendImageMessagePayload {
  groupName: string;
  filename: string;
  base64EncodedImage: string;
}

export interface RequestSuggestionsPayload {
  groupName: string;
  k: number;
  messages: string[];
  image_urls: string[];
} 

