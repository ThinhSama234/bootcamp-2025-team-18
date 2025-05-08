import api from './axios';
import { formatTimeAgo } from '../utils/formatTimeAgo';

export const fetchGroupList = async (username) => {
  try {
    const response = await api.get('/api/v1/groups/' + username);

    // Expecting a structure with { domainCode, message, data: [...] }
    const groupData = response.data?.data || [];

    // Optional: map or sanitize data if needed
    const formattedGroups = groupData.map(group => ({
      id: group.id,
      groupName: group.groupName,
      lastMessage: group.lastMessageContent,
      timestamp: formatTimeAgo(group.lastMessageTime),
      members: group.members,
      groupPicSrc: '/group1.jpg'
    }));

    return formattedGroups;
  } catch (error) {
    console.error('Error fetching group list:', error);
    return [];
  }
};

export const fetchMessages = async (groupName) => {
    try {
        const response = await api.get('/api/v1/messages/' + groupName);
    
        // Expecting a structure with { domainCode, message, data: [...] }
        const messageData = response.data?.data || [];
    
        // Optional: map or sanitize data if needed
        const formattedMessages = messageData.map(message => ({
        id: message.id,
        sender: message.senderUsername,
        content: message.messageContent,
        timestamp: new Date(message.createdAt).toLocaleString(),
        }));
    
        return formattedMessages;
    } catch (error) {
        console.error('Error fetching messages:', error);
        return [];
    }
}

export const createGroup = async (groupName, creator) => {
    try {
        const response = await api.post('/api/v1/groups', {
            groupName : groupName,
            creator : creator,
        });
    
        // Expecting a structure with { domainCode, message, data: [...] }
        const groupData = response.data?.data || null;
    
        return groupData;
    } catch (error) {
        console.error('Error creating group:', error);
        return null;
    }
}