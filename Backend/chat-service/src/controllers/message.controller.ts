import { Request, Response } from "express";
import { OKResponse } from "../core/responses/SuccessResponse";
import { matchedData } from "express-validator";
import { IMessageService } from "../services/message.service";
import messageService from "../services/impl/message.service";
import { MessageQuery } from "../types/message.types";

export class MessageController {
  constructor(private readonly messageService: IMessageService) {}

  async getMessages(req: Request, res: Response) {
    const query = matchedData(req) as MessageQuery;
    const messages = await this.messageService.getMessagesByGroupName(query);
    new OKResponse({ data: messages }).send(res);
  }

  // async getUserGroups(req: Request, res: Response) {
  //   const { username } = matchedData(req);
  //   const groups = await this.messageService.getAllGroupsByUsernameOrderByLastMessageCreationTime(username);
  //   new OKResponse({ data: groups }).send(res);
  // }

}

export default new MessageController(messageService);