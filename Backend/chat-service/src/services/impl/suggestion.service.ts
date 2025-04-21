import { ISuggestionService } from '../suggestion.service'

class SuggestionService implements ISuggestionService {
  async initSuggestionRequest(k: number, messages: string[]): Promise<string> {
    throw new Error('Method not implemented.');
    // get suggestion id from suggestion service server
    // return suggestion id
  }

  async getSingleSuggestion(suggestionId: string): Promise<string> {
    throw new Error('Method not implemented.');
    // get suggestion from suggestion service server
    // return suggestion
  }
}

export default new SuggestionService();