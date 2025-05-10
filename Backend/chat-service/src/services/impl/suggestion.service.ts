import dotenv from 'dotenv';
dotenv.config();

import { LocationClient } from '../../modules/grpc/clients';
import { ISuggestionService } from '../suggestion.service'


class SuggestionService implements ISuggestionService {
  private client: LocationClient;
  
  constructor(URL: string) {
    this.client = new LocationClient(URL);
  }

  getSuggestions(k: number, messages: string[], image_urls: string[], coordinates: { latitude: number, longtitude: number } | undefined, initCb: Function, getSingleSuggestionCb: Function, errorCb?: Function): void {
    this.client.getSuggestions(k, messages, image_urls, coordinates, initCb, getSingleSuggestionCb, errorCb);
  }

}

const URL = process.env.LOCATION_SERVICE_GRPC_URL;
if (!URL)
  throw new Error('Location service URL is not defined in environment variables');
export default new SuggestionService(URL);