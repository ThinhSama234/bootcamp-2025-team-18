
export interface ISuggestionService {
  initSuggestionRequest: (groupName: string,  k: number, messages: string[]) => Promise<string>;

  getSingleSuggestion: (suggestionId: string) => Promise<string>;
}