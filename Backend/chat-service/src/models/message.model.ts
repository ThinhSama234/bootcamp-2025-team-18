import mongoose from "mongoose";

export const MessageTypes = ["text", "image", "file"];

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
    default: "text",
  },
  content: {
    type: String,
    required: true,
    trim: true
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