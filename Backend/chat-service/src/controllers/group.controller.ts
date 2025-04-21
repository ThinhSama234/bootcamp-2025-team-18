import { matchedData } from "express-validator";
import { IGroupService } from "../services/group.service";
import groupService from "../services/impl/group.service";
import { CreatedResponse } from "../core/responses/SuccessResponse";


class GroupController {
  constructor(private readonly groupService: IGroupService) {}

  async createGroup(req: any, res: any) {
    const { groupName, creator } = matchedData(req);
    await this.groupService.createGroup(groupName);
    const group = await this.groupService.addUserToGroup(groupName, creator);
    new CreatedResponse({ message: "Group created successfully", data: group }).send(res);
  }

  async getGroupsByUsername(req: any, res: any) {
    const { username } = matchedData(req);
    const groups = await this.groupService.getGroupsByUsername(username);
    new CreatedResponse({ message: "Groups fetched successfully", data: groups }).send(res);
  }

}

export default new GroupController(groupService)