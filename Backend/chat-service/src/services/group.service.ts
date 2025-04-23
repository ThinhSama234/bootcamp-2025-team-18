import { GroupType } from "../types/group.types";

export interface IGroupService {
  createGroup(groupName: string): Promise<GroupType>;
  
  getGroupsByUsername(username: string): Promise<GroupType[]>;
  
  getGroupByName(groupName: string): Promise<GroupType>;

  addUserToGroup(groupName: string, username: string): Promise<GroupType>;
  
  removeUserFromGroup(groupName: string, username: string): Promise<GroupType>;

  updateLastMessage(groupName: string, lastMessageContent: any, lastMessageTime: Date): Promise<GroupType>;

  // deleteGroup(groupName: string): Promise<GroupType>;
}