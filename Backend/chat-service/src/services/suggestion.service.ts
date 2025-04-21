
export interface ISuggestionService {
  initSuggestionRequest: (k: number, messages: string[]) => Promise<string>;

  getSingleSuggestion: (suggestionId: string) => Promise<string>;
}