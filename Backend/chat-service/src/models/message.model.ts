import mongoose from "mongoose";
import { MessageType } from "../types/message.types";


export const MessageTypes = Object.values(MessageType);

const messageSchema = new mongoose.Schema({
  senderUsername: {
    type: String,
    required: true,
  },
  groupName: {
    type: String,
    required: true,
  },
  messageType: {
    type: String,
    enum: MessageTypes,
    required: true,
    default: MessageType.TEXT,
  },
  content: {
    type: mongoose.Schema.Types.Mixed,
    required: true,
  },
}, {
  timestamps: true,
})
.index({
  groupName: 1,
  createdAt: -1,
});

const Message = mongoose.model("Message", messageSchema);
export default Message;