
if (!process.env.CHATDB_URL) {
  throw new Error("CHATDB_URL is not defined in .env file");
}

export const CHATDB_URL = process.env.CHATDB_URL;