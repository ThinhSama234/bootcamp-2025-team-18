import mongoose from "mongoose";


const GroupSchema = new mongoose.Schema({
  groupName: {
    type: String,
    required: true,
    unique: true,
  },
  members: {
    type: [String],
    required: true,
  },
  lastMessageContent: {
    type: mongoose.Schema.Types.Mixed,
    required: false,
  },
  lastMessageTime: {
    type: Date,
    required: false,
  },
})
.index({ lastMessageTime: -1 });

const Group = mongoose.model("Group", GroupSchema);
export default Group;