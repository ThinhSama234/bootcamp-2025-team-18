import { DomainCode } from "../../core/responses/DomainCode";
import { BadRequestError, NotFoundError } from "../../core/responses/ErrorResponse";
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
    const existingGroup = await Group.find({ groupName });
    if (existingGroup.length === 0)
      throw new NotFoundError(DomainCode.NOT_FOUND, 'Group does not exist!');

    if (existingGroup[0].members.includes(username))
      throw new BadRequestError(DomainCode.FORBIDDEN, 'User already in group!');

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

  async updateLastMessage(groupName: string, lastMessageContent: any, lastMessageTime: Date): Promise<GroupType> {
    const group = await Group.findOneAndUpdate(
      { groupName: groupName },
      { lastMessageContent, lastMessageTime },
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
      lastMessageContent: doc.lastMessageContent,
      lastMessageTime: doc.lastMessageTime,
      members: doc.members,
    };
  }
}

export default new GroupService();
