import dotenv from 'dotenv';
dotenv.config();

import { LocationClient } from '../../grpc/clients';
import { ISuggestionService } from '../suggestion.service'
import Group from '../../models/group.model';
import { NotFoundError } from '../../core/responses/ErrorResponse';
import { DomainCode } from '../../core/responses/DomainCode';


class SuggestionService implements ISuggestionService {
  private client: LocationClient;
  
  constructor(URL: string) {
    this.client = new LocationClient(URL);
  }

  async initSuggestionRequest(groupName: string, k: number, messages: string[]): Promise<string> {
    // check group exist
    const group = await Group.findOne({ groupName });
    if (!group) {
      throw new NotFoundError(DomainCode.NOT_FOUND, 'Group does not exist');
    }
    return await this.client.initSuggestionRequest(groupName, k, messages);
  }

  async getSingleSuggestion(suggestionId: string): Promise<string> {
    return await this.client.getSingleSuggestion(suggestionId);
  }
}

const URL = process.env.LOCATION_SERVICE_GRPC_URL;
if (!URL)
  throw new Error('Location service URL is not defined in environment variables');
export default new SuggestionService(URL);