
export interface ISuggestionService {
  getSuggestions: (k: number, messages: string[], image_urls: string[], coordinates: { latitude: number, longtitude: number } | undefined, initCb: Function, getSingleSuggestionCb: Function, errorCb?: Function) => void;
}