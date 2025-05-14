import  { useRef, use, useState, useEffect } from 'react';
import './MainChat.css'; 
import Avatar from './common/Avatar';
import Message from './common/Message';
import { ShareMediaModal } from './common/Modal';
import { fetchMessages } from '../api/groupService';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../context/SocketContext';
import { Modal } from 'antd';
import 'antd/dist/reset.css';  // or the appropriate antd css import based on your version

function ChatWindow({group}) {
  const { username} = useAuth();
  const { sendMessage, requestSuggestions, socket } = useSocket();

  const [showShareMediaModal, setShareMediaModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [zoomedImg, setZoomedImg] = useState(null);
  const [selectedMessages, setSelectedMessages] = useState([]);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [suggestionList, setSuggestionList] = useState([]);


  const suggestionListRef = useRef(suggestionList);

  useEffect(() => {
    suggestionListRef.current = suggestionList;
  }, [suggestionList]);

  const messagesRef = useRef(messages);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);


  const closeModal = () => {
    setZoomedImg(null);
  };

  useEffect(() => {
    if (!group) return; 

    const getMessages = async () => {
      try {
        const fetchedMessages = await fetchMessages(group.groupName);
        console.log("Fetched messages:", fetchedMessages);
        const tranformedMessages = fetchedMessages.map(msg => {
          if (msg.type === 'suggestions') {
            return msg.suggestions.map((suggestionText, index) => ({
            id: `${msg.suggestionId}-${index}`, // ensure unique IDs
            sender: 'Gravel',
            content: suggestionText,
            timestamp: new Date(msg.createdAt).toLocaleString(),
            type: 'text',
          }));
          } else {
            return msg;
          }
        });

        console.log("Transformed messages:", tranformedMessages);
        setMessages(tranformedMessages);
        console.log("Get messages:", messages);
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
      console.log("Received message:");
      // Optional: Filter to ignore messages from other groups
      if (msg.groupName === group.groupName) {
        if (msg.messageType === 'suggestions' && Array.isArray(msg.suggestions)) {
          // const newSuggestionMessages = msg.suggestions.map((suggestionText, index) => ({
          //   id: `${msg.suggestionId}-${index}`, // ensure unique IDs
          //   sender: 'Gravel',
          //   content: suggestionText,
          //   timestamp: new Date(msg.createdAt).toLocaleString(),
          //   type: 'text',
          // }));

          // setMessages(prev => [...newSuggestionMessages, ...prev]);
        }
        else {
          setMessages(prev => [
          {
            id: msg.id || `socket-${Date.now()}`,
            sender: msg.senderUsername,
            content: msg.messageType === 'image' ? msg.imageUrl : msg.messageContent,
            timestamp: new Date(msg.createdAt).toLocaleString(),
            type: msg.messageType,
          },
          ...prev
          ]);
        }
      }
    };

    const handleReceiveSuggestionId = (msg) => {
      console.log("Received suggestion ID:");
      // Optional: Filter to ignore messages from other groups
      // setMessages(prev => [
      //   {
      //     id: msg.suggestionId || `socket-${Date.now()}`,
      //     sender: "Gravel",
      //     content: "Hi! I am Gravel, your AI assistant. I have some suggestions for you.",
      //     timestamp: Date.now().toLocaleString(),
      //     type: 'text',
      //   },
      //   ...prev
      // ]);
    }

    const handleReceiveSuggestion = (msg) => {
      const suggestionKey = `${msg.suggestionId}-${msg.rank}`;

      if (suggestionListRef.current.includes(suggestionKey)) {
        return; // Already processed
      }

      console.log('handleReceiveSuggest');
      console.log(suggestionListRef.current);
      console.log(suggestionKey);
      console.log(messagesRef.current);
      
      // Add message
      setMessages(prev => [
        {
          id: suggestionKey,
          sender: "Gravel",
          content: msg.suggestion,
          timestamp: new Date(msg.timestamp).toLocaleString(),
          type: 'text',
        },
        ...prev
      ]);

      // Add to suggestion list
      setSuggestionList(prevList => [...prevList, suggestionKey]);
    };



    socket.on('receive_message', handleReceiveMessage);
    socket.on('receive_suggestion_id', handleReceiveSuggestionId);
    socket.on('receive_suggestion', handleReceiveSuggestion);

    return () => {
      socket.off('receive_message', handleReceiveMessage);
      socket.off('receive_suggestion_id', handleReceiveSuggestionId);
      socket.off('receive_suggestion', handleReceiveSuggestion);
    };
  }, [socket, group]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Emit socket message
    sendMessage(group.groupName, inputValue);

    setInputValue('');
  };

  const handleRequestButtonClick = () => {
    // if (selectedMessages.length === 0) {
    //   Modal.warning({
    //     title: 'No Messages Selected',
    //     content: 'Please select at least one message to get suggestions',
    //   });
    //   return;
    // }
    setShowConfirmModal(true);
  };

  const handleRequestSuggestions = () => {
    console.log("Requesting suggestions...");
    const k = 5;
    const selected = messages.filter(msg => selectedMessages.includes(msg.id));
    console.log("Selected messages:", selected);
    console.log("Selected message IDs:", selectedMessages);
    const imageUrls = selected.filter(msg => msg.type === 'image').map(msg => msg.content);
    console.log("Image URLs:", imageUrls);
    const messagesToSent = selected.filter(msg => msg.type === 'text').map(msg => msg.content); 
    console.log("Messages:", messagesToSent);
    const coordinates = null;
    requestSuggestions(group.groupName, k, messagesToSent, imageUrls);
    console.log("Request sent");
  };

  const handleSelectMessage = (id) => {
    setSelectedMessages(prev =>
      prev.includes(id) ? prev.filter(mid => mid !== id) : [...prev, id]
    );
  };

  if (loading || !group) {
    return (
      <div className="loading-screen">
        <img src="/loading.gif" alt="Loading..." className="loading-gif" />
      </div>
    );
  }

  console.log("Main Chat Reloaded");

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
              isPicture={msg.type === 'image'}
              onClick={() => msg.type === 'image' && setZoomedImg(msg.content)}
              id={msg.id}
              onSelect={handleSelectMessage}
              isSelected={selectedMessages.includes(msg.id)}
            />
          )) : <p className='no-messages'>No messages yet. Say something to other members.</p>}
      </div>
      
      <div className="chat-input">
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
        <button className='send-button' title='Send' onClick={handleRequestButtonClick}>
          <img src='/Gravel.png' alt='Send icon' className='send-icon' />
        </button>
      </div>

      <Modal
        title="Request Suggestions"
        open={showConfirmModal}
        onOk={() => {
          handleRequestSuggestions();
          setShowConfirmModal(false);
        }}
        onCancel={() => setShowConfirmModal(false)}
        okText="Confirm"
        cancelText="Cancel"
        okButtonProps={{ 
          style: { 
            background: 'linear-gradient(90deg, #09ad4f, #78d59f)',
            border: 'none' 
          } 
        }}
      >
        <p>Are you sure you want to request suggestions for the selected messages?</p>
      </Modal>

      {showShareMediaModal && <ShareMediaModal onClose={() => setShareMediaModal(false)} />}
      {zoomedImg && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content">
            <img src={zoomedImg} alt="Zoomed" />
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatWindow;