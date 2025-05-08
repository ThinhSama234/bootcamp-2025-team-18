
export interface IImageService {
  decodeBase64Image(base64Image: string): { mimeType: string; buffer: Buffer };
  uploadImage(filename: string, image: Buffer, mimeType: string): Promise<{key: string; imageUrl: string}>;
  deleteImage(key: string): Promise<void>;
}