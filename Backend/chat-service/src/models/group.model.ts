import mongoose from "mongoose";


const GroupSchema = new mongoose.Schema({
  groupName: {
    type: String,
    required: true,
  },
  members: {
    type: [String],
    required: true,
  },
  lastMessage: {
    type: mongoose.Schema.Types.Mixed,
    required: false,
  },
  lastMessageTime: {
    type: Date,
    required: false,
  },
})
.index({ groupName: 1 })
.index({ lastMessageTime: -1 });

const Group = mongoose.model("Group", GroupSchema);
export default Group;