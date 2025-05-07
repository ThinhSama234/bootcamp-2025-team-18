import AWS from 'aws-sdk';
import { DO_SPACES_ACCESS_KEY, DO_SPACES_ENDPOINT, DO_SPACES_SECRET } from '../config/do.config';

const s3 = new AWS.S3({
  endpoint: DO_SPACES_ENDPOINT,
  accessKeyId: DO_SPACES_ACCESS_KEY,
  secretAccessKey: DO_SPACES_SECRET,
});

export default s3;