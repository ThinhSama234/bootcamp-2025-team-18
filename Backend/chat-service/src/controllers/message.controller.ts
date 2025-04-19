import { Request, Response } from "express";
import { CreatedResponse, OKResponse, NoContentResponse } from "../core/responses/SuccessResponse";
import { matchedData } from "express-validator";
import { IMessageService } from "../services/message.service";
import messageService from "../services/impl/message.service";
import { Message, MessageQuery } from "../types/message.types";

export class MessageController {
  constructor(private readonly messageService: IMessageService) {}

  async createMessage(req: Request, res: Response) {
    const messageData = matchedData(req) as Omit<Message, "id" | "createdAt" | "updatedAt">;
    const message = await this.messageService.createMessage(messageData);
    new CreatedResponse({ data: message }).send(res);
  }

  async getMessages(req: Request, res: Response) {
    const query = matchedData(req) as MessageQuery;
    const messages = await this.messageService.getMessagesByGroupName(query);
    new OKResponse({ data: messages }).send(res);
  }

  async getUserGroups(req: Request, res: Response) {
    const { username } = matchedData(req);
    const groups = await this.messageService.getAllGroupsByUsernameOrderByLastMessageCreationTime(username);
    new OKResponse({ data: groups }).send(res);
  }

  async updateMessage(req: Request, res: Response) {
    const { messageId } = req.params;
    const { content } = matchedData(req);
    const message = await this.messageService.updateMessageContent(messageId, content);
    new OKResponse({ data: message }).send(res);
  }

  async deleteMessage(req: Request, res: Response) {
    const { messageId } = matchedData(req);
    await this.messageService.deleteMessage(messageId);
    new NoContentResponse({}).send(res);
  }
}

export default new MessageController(messageService);