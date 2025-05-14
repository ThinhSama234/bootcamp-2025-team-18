import React, { use, useState, useEffect } from 'react';
import './GroupList.css';
import Group from './common/Group';
import { JoinGroupModal } from './common/Modal';
import { useSocket } from '../context/SocketContext';

function SidebarLeft({groupList, onGroupSelect, selectedGroupName, refreshGroupList}) {
  const [showModal, setShowModal] = React.useState(false);
  const { socket } = useSocket();

  console.log(groupList);
  console.log(selectedGroupName);

  useEffect(() => {
    if (!socket) return;

    const currentUsername = localStorage.getItem('username');
    console.log(currentUsername)

    const handleUserJoined = (data) => {
      if (data.username === currentUsername) {
        refreshGroupList();
      }
    };

    const handleReceiveMessage = () => {
      refreshGroupList();
    };

    socket.on('user_joined', handleUserJoined);
    socket.on('receive_message', handleReceiveMessage);
    socket.on()

    return () => {
      socket.off('user_joined', handleUserJoined);
      socket.off('receive_message', handleReceiveMessage);
    };
  }, [socket, refreshGroupList]);

  return (
    <div className="sidebar-left">

      <div className="group-list-header">
        <h2>Group Chats</h2>
        <button className="join-group-button" title="Create Group" onClick= {() => setShowModal(true)}>
          <img src="/join-group-icon.png" alt="Join Group" className="join-group-icon" />
        </button>
      </div>

      {showModal && <JoinGroupModal onClose={() => setShowModal(false)} />}

      <div className="group-search">
        <input type="text" placeholder="Search groups..." className="search-input" />
        {/* TODO: add search functionality */}
        <button className="search-button" title="Search" onClick={() => alert('Search for groups!')}>
          <img src="/search-icon.png" alt="Search" className="search-icon" />
        </button>
      </div>

      {/* TODO: retrieve group list from server */}
      <div className="group-list">
        { !groupList ? <h4>Create new groups and add your friends!</h4> : groupList.map((group, index) => (
          <Group
            key={index}
            groupName={group.groupName}
            groupPicSrc={group.groupPicSrc}
            lastMessage={group.lastMessage}
            timestamp={group.timestamp}
            onClick={() => onGroupSelect(group)}
            isSelected={group.groupName === selectedGroupName}
          />
        ))} 
      </div>
    </div>
  );
}

export default SidebarLeft;
