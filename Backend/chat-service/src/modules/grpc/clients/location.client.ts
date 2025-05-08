import { credentials, ServiceError } from '@grpc/grpc-js';
import { loadProto } from '../loader';
import logger from '../../../core/logger';
import path from 'path';

interface SuggestionRequest {
  k: number;
  messages: string[];
}

interface SuggestionReply {
  type: string;
  content: string;
}

export class LocationClient {
  private client: any;
  private calls: any[];

  constructor(address: string) {
    const proto = loadProto(path.join(import.meta.dirname, '../proto/location_service.proto'));
    this.client = new proto.Location.Suggestion(
      address,
      credentials.createInsecure()
    );
    this.calls = [];
  }

  async getSuggestions(k: number, messages: string[], initCb: Function, getSingleSuggestionCb: Function, errorCb?: Function) {
    const request: SuggestionRequest = { k, messages };
    const call = this.client.GetSuggestions(request);
    this.calls.push(call);
    
    let suggestionId: string | null = null;
    call.on('data', async (response: SuggestionReply) => {
      if (response.type === 'INIT') {
        await initCb(response.content);
        suggestionId = response.content;
      } 
      else if (response.type === 'SUGGESTION') {
        while (suggestionId === null) {
          await new Promise(resolve => setTimeout(resolve, 10));
        }
        await getSingleSuggestionCb(suggestionId, response.content);
      }
    });
    
    call.on('end', () => {
      this.calls = this.calls.filter((c: any) => c !== call);
    });

    call.on('error', (error: ServiceError) => errorCb ? errorCb(error) : logger.error(`${error}`));
  }
}