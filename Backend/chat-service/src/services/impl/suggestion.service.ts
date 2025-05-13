import { LOCATION_SERVICE_GRPC_URL } from '../../config/suggestionService';
import { LocationClient } from '../../modules/grpc/clients';
import { ISuggestionService } from '../suggestion.service'


class SuggestionService implements ISuggestionService {
  constructor(private readonly client: LocationClient) {
    this.client = client;
  }

  getSuggestions(k: number, messages: string[], image_urls: string[], coordinates: { latitude: number, longtitude: number } | undefined, initCb: Function, getSingleSuggestionCb: Function, errorCb?: Function): void {
    this.client.getSuggestions(k, messages, image_urls, coordinates, initCb, getSingleSuggestionCb, errorCb);
  }

}

export default new SuggestionService(new LocationClient(LOCATION_SERVICE_GRPC_URL));