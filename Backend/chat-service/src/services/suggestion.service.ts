
export interface ISuggestionService {
  getSuggestions: (k: number, messages: string[], initCb: Function, getSingleSuggestionCb: Function, errorCb?: Function) => void;
}