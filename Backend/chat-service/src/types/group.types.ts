export interface GroupType {
  id: string;
  groupName: string;
  members: string[];
  lastMessageContent?: any;
  lastMessageTime?: Date;
}