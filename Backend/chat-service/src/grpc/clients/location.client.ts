import { credentials, ServiceError } from '@grpc/grpc-js';
import { PROTO_PATH } from '../config/config';
import { loadProto } from '../loader';

interface InitRequest {
  group_name: string;
  k: number;
  messages: string[];
}

interface InitReply {
  suggestionId: string;
}

interface SuggestionRequest {
  suggestionId: string;
}

interface SuggestionReply {
  suggestion: string;
}

export class LocationClient {
  private client: any;

  constructor(address: string) {
    const proto = loadProto(PROTO_PATH);
    this.client = new proto.Location.Suggestion(
      address,
      credentials.createInsecure()
    );
  }

  async initSuggestionRequest(groupName: string, k: number, messages: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const req: InitRequest = {
        group_name: groupName,
        k,
        messages,
      };
      this.client.InitSuggestionRequest( req, (error: ServiceError | null, response: InitReply) => {
        if (error) {
          reject(error);
          return;
        }
        resolve(response.suggestionId);
      });
    });
  }

  async getSingleSuggestion(suggestionId: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const req: SuggestionRequest = {
        suggestionId
      };
      this.client.GetSingleSuggestion(req, (error: ServiceError | null, response: SuggestionReply) => {
        if (error) {
          reject(error);
          return;
        }
        resolve(response.suggestion);
      });
    });
  }
  
}