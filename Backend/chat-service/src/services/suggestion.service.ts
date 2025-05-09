
export interface ISuggestionService {
  getSuggestions: (k: number, messages: string[], image_urls: string[], initCb: Function, getSingleSuggestionCb: Function, errorCb?: Function) => void;
}