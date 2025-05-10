import React, { useEffect } from 'react';
import './ChatInfo.css'; // Assuming you have a CSS file for styling
import {GroupSettings, MemberList, SharedMedia} from './common/DropDown';
import { fetchMessages } from '../api/groupService';
import { useSocket } from '../context/SocketContext';

function SidebarRight({group}) {
  const [loading, setLoading] = React.useState(true);
  const [groupMembers, setGroupMembers] = React.useState(null);
  const [picSrcList, setPicSrcList] = React.useState(null);
  const { receiveMessage, socket } = useSocket(); 

  useEffect(() => {
    if (!group) return; 

    const getMessages = async () => {
      try {
        const messages = await fetchMessages(group.groupName);
        const lis = messages.filter(message => message.type === 'image').map(message => message.content);
        // console.log("[ChatInfo.jsx] Messages: ", messages);
        // console.log("[ChatInfo.jsx] Temp Image URL List: ", lis);
        setPicSrcList(lis);
      } catch (err) {
        console.error("Failed to fetch messages:", err);
      } finally {
        // console.log("[ChatInfo.jsx] After getMessages - Image URL List: ", picSrcList);
        setLoading(false);
      }
    };

    const getGroupDetails = async () => {
      try {
        getMessages();

        setGroupMembers(group.members.map((member) => {
          return {
            name: member,
            pic: 'thisuser.jpg' // Fallback to default image if not available
          };
        }));
        // console.log("[ChatInfo.jsx] Group members:", groupMembers);
      } catch (err) {
        console.error("Failed to fetch group details:", err);
      } finally {
        // console.log("[ChatInfo.jsx] Image URL List: ", picSrcList);
        localStorage.setItem('groupName', group.groupName);
        setLoading(false);
      }
    };

    getGroupDetails();
  } , [group, receiveMessage, socket]);
  
  if (loading || !group) {
    return (
      <div className="loading-screen">
        <img src="/loading.gif" alt="Loading..." className="loading-gif" />
      </div>
    );
  }

  // console.log("[ChatInfo.jsx] Final Image URL List: ", picSrcList);
  return (
    <div className="sidebar-right">
      <img src="/group1.jpg" alt="Group" className="group-pic-large" />
      <h3>{group.groupName}</h3>

      <GroupSettings header="Group Settings" />
      {
        groupMembers && <MemberList members={groupMembers} />
      }

      <SharedMedia mediaData={{
        May: picSrcList,
      }} />
    

      
    </div>
  );
}

export default SidebarRight;
