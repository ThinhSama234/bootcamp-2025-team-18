import { DO_SPACE_NAME } from "../../config/do.config";
import logger from "../../core/logger";
import { DomainCode } from "../../core/responses/DomainCode";
import { BadRequestError } from "../../core/responses/ErrorResponse";
import s3 from "../../database/s3";
import { IImageService } from "../image.service";

import { v4 as uuid } from "uuid";

class ImageService implements IImageService {
  decodeBase64Image(base64Image: string): { mimeType: string; buffer: Buffer; } {
    const matches = base64Image.match(/^data:(.+);base64,(.+)$/);
    if (!matches) {
      throw new BadRequestError(DomainCode.INVALID_INPUT_FIELD, 'Invalid base64 image format');
    }

    const mimeType = matches[1];
    const base64Data = matches[2];
    const buffer = Buffer.from(base64Data, 'base64');

    return { mimeType: mimeType.split(':')[1], buffer }; 
  }

  async uploadImage(filename: string, image: Buffer, mimeType: string): Promise<{ key: string; imageUrl: string }> {
    const key = `uploads/${uuid()}-${filename}`;
    const uploadParms = {
      Bucket: DO_SPACE_NAME,
      Key: key,
      Body: image,
      ACL: 'public-read',
      ContentEncoding: 'base64',
      ContentType: mimeType,
    }

    const result = await s3.upload(uploadParms).promise();
    logger.info(`Image uploaded to ${result.Location}`);

    return {
      key: key,
      imageUrl: result.Location,
    }
  }

  async deleteImage(key: string): Promise<void> {
    const result = await s3
      .deleteObject({
        Bucket: DO_SPACE_NAME,
        Key: key,
      })
      .promise();

    logger.info(`Image deleted from ${key}`);
  }
}

export default new ImageService();