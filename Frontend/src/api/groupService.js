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
      lastMessage: typeof group.lastMessageContent === 'string' ? group.lastMessageContent :  '[Image]',
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

    console.log("Response from fetchMessages:", response);

    const messageData = response.data?.data || [];

    const formattedMessages = [];

    for (const message of messageData) {
      if (message.messageType === 'suggestions' && Array.isArray(message.suggestions)) {
        // Flatten each suggestion string into a separate message
        message.suggestions.forEach((suggestionText, index) => {
          formattedMessages.push({
            id: `${message.id}-sugg-${index}`,
            sender: 'Gravel',
            content: suggestionText,
            timestamp: new Date(message.createdAt).toLocaleString(),
            type: 'text',
          });
        });
      } else {
        // Normal message
        formattedMessages.push({
          id: message.id,
          sender: message.senderUsername,
          content: message.messageType === 'image' ? message.imageUrl : message.messageContent,
          timestamp: new Date(message.createdAt).toLocaleString(),
          type: message.messageType,
        });
      }
    }

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