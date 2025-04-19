import React from 'react';

function ChatWindow({groupName}) {
  return (
    <div className="main-chat">
      <div className="chat-header">
        <h3>{groupName}</h3>
      </div>
      <div className="chat-messages">
        <div className="message sent">Hey everyone!</div>
        <div className="message received">Hello!</div>
      </div>
      <div className="chat-input">
        <input type="text" placeholder="Type a message..." />
        <button>Send</button>
      </div>
    </div>
  );
}

export default ChatWindow;
