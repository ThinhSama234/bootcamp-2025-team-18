// src/context/SocketContext.jsx
import React, { createContext, useContext, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

const SocketContext = createContext(null);

export const useSocket = () => {
  return useContext(SocketContext);
};

export const SocketProvider = ({ username, children }) => {
  const socketRef = useRef(null);

  useEffect(() => {
    if (username) {
      socketRef.current = io('http://137.184.249.25:3000/', {
        auth: { 'username': username },
      });

      socketRef.current.on('connect', () => {
        console.log('Connected to socket server');
      });

      socketRef.current.on('error', (error) => {
        console.error('Socket error:', error);
      });

      socketRef.current.on('user_joined', (data) => {
        console.log('User joined:', data);
      });

      socketRef.current.on('user_left', (data) => {
        console.log('User left:', data);
      });

      socketRef.current.on('receive_message', (message) => {
        console.log('Received message:', message);
      });

      socketRef.current.on('receive_suggestion_id', (data) => {
        console.log('Received suggestion ID:', data);
      });

      socketRef.current.on('receive_suggestion', (data) => {
        console.log('Received suggestion:', data);
      });

      return () => {
        socketRef.current.disconnect();
      };
    }
  }, [username]);

  const joinGroup = (groupName) => {
    socketRef.current.emit('join_group', { 'groupName' : groupName });
  };

  const leaveGroup = (groupName) => {
    socketRef.current.emit('leave_group', { 'groupName' : groupName });
  };

  const sendMessage = (groupName, content) => {
    socketRef.current.emit('send_text_message', { 'groupName' : groupName, 'content' : content });
  };

  const requestSuggestions = (groupName, k, messages) => {
    socketRef.current.emit('request_suggestions', { 'groupName' : groupName, 'k' : k, 'messages' : messages });
  };

  return (
    <SocketContext.Provider
      value={{
        socket: socketRef.current,
        joinGroup,
        leaveGroup,
        sendMessage,
        requestSuggestions,
      }}
    >
      {children}
    </SocketContext.Provider>
  );
};
