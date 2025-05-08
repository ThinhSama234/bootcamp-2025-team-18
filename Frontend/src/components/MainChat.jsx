import React, { use, useEffect } from 'react';
import './MainChat.css'; 
import Avatar from './common/Avatar';
import Message from './common/Message';
import { ShareMediaModal } from './common/Modal';
import { fetchMessages } from '../api/groupService';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../context/SocketContext';

function ChatWindow({group}) {
  const { username} = useAuth();
  const { sendMessage, socket } = useSocket();

  const [showShareMediaModal, setShareMediaModal] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [messages, setMessages] = React.useState([]);
  const [inputValue, setInputValue] = React.useState('');

  useEffect(() => {
    if (!group) return; 

    const getMessages = async () => {
      try {
        const messages = await fetchMessages(group.groupName);
        setMessages(messages);
      } catch (err) {
        console.error("Failed to fetch messages:", err);
      } finally {
        setLoading(false);
      }
    };

    getMessages();
  }, [group.groupName]); 

  // Listen for new messages from the socket
  useEffect(() => {
    if (!socket || !group) return;

    const handleReceiveMessage = (msg) => {
      // Optional: Filter to ignore messages from other groups
      if (msg.groupName === group.groupName) {
        setMessages(prev => [
        {
          id: msg.id || `socket-${Date.now()}`,
          content: msg.messageContent,
          sender: msg.senderUsername
        },
        ...prev
      ]);
      }
    };

    socket.on('receive_message', handleReceiveMessage);

    return () => {
      socket.off('receive_message', handleReceiveMessage);
    };
  }, [socket, group]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Emit socket message
    sendMessage(group.groupName, inputValue);

    setInputValue('');
  };

  if (loading || !group) {
    return (
      <div className="loading-screen">
        <img src="/loading.gif" alt="Loading..." className="loading-gif" />
      </div>
    );
  }

  console.log(messages);

  return (
    <div className="main-chat">

      <div className="chat-header">
        <div className="chat-header-group-info">
          <Avatar src={group.groupPicSrc} alt="Group Pic" size="large"/>
          <h3>{group.groupName}</h3>
        </div>
        <button className="chat-header-button" title="Group Info" onClick={() => alert('Group Info')}>
          <img src="/group-info-icon.png" alt="Info" className="info-icon" />
        </button>
      </div>
      
      <div className="chat-messages">
        {messages.length !== 0 ? messages.map(msg => (
            <Message
              senderPic='thisuser.jpg'
              key={msg.id}
              senderName={msg.sender}
              content={msg.content}
              isSent={msg.sender === username}
              timestamp={msg.timestamp}
            />
          )) : <p className='no-messages'>No messages yet. Say something to other members.</p>}
      </div>
      
      <div className="chat-input">
        <button className='request-button' title='Request Recommend' onClick={() => alert('Request Recommend')}>
          <img src='/request-icon.png' alt='Request icon' className='request-icon' />
        </button>
        <button className='add-media-button' title='Add Media' onClick={() => setShareMediaModal(true)}>
          <img src='/media-icon.png' alt='Add media icon' className='add-media-icon' />
        </button>
        <input 
          type="text"
          placeholder="Type a message..."
          value = {inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          />
        <button className='send-button' title='Send' onClick={handleSendMessage}>
          <img src='/send-icon.png' alt='Send icon' className='send-icon' />
        </button>
      </div>
      {showShareMediaModal && <ShareMediaModal onClose={() => setShareMediaModal(false)} />}
    </div>
  );
}

export default ChatWindow;
