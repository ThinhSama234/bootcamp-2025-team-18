import { DomainCode } from "../../core/responses/DomainCode";
import { NotFoundError } from "../../core/responses/ErrorResponse";
import Group from "../../models/group.model";
import { GroupType } from "../../types/group.types";
import { IGroupService } from "../group.service";


class GroupService implements IGroupService {
  async createGroup(groupName: string): Promise<GroupType> {
    const existingGroup = await Group.find({ groupName });
    if (existingGroup.length > 0) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Group already exists");
    }

    const groupDoc = await new Group({ groupName }).save();

    return this.toGroup(groupDoc);
  }

  async getGroupsByUsername(username: string): Promise<GroupType[]> {
    const groups = await Group.find({
      members: username
    }).sort({ lastMessageTime: -1 });

    return groups.map(group => this.toGroup(group));
  }

  async addUserToGroup(groupName: string, username: string): Promise<GroupType> {
    const group = await Group.findOneAndUpdate(
      { groupName: groupName },
      { $addToSet: { members: username } },
      { new: true }
    );
    if (!group) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Group not found");
    }
    return this.toGroup(group); 
  }

  async removeUserFromGroup(groupName: string, username: string): Promise<GroupType> {
    const group = await Group.findOneAndUpdate(
      { groupName: groupName },
      { $pull: { members: username } },
      { new: true }
    );
    if (!group) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Group not found");
    }
    return this.toGroup(group);
  }

  async updateLastMessage(groupName: string, lastMessage: string, lastMessageTime: Date): Promise<GroupType> {
    const group = await Group.findOneAndUpdate(
      { groupName: groupName },
      { lastMessage, lastMessageTime },
      { new: true }
    );
    if (!group) {
      throw new NotFoundError(DomainCode.NOT_FOUND, "Group not found");
    }
    return this.toGroup(group);
  }
  
  // async deleteGroup(groupName: string): Promise<GroupType> {
  //   const group = await Group.findOneAndDelete({ groupName });
  //   if (!group) {
  //     throw new NotFoundError(DomainCode.NOT_FOUND, "Group not found");
  //   }
  //   return this.toGroup(group);
  // }

  private toGroup(doc: any): GroupType {
    return {
      id: doc._id.toString(),
      groupName: doc.groupName,
      lastMessage: doc.lastMessage,
      lastMessageTime: doc.lastMessageTime,
      members: doc.members,
    };
  }
}

export default new GroupService();
