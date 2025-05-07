import React, { useState } from 'react';
import './GroupList.css';
import Group from './common/Group';
import { JoinGroupModal } from './common/Modal';

function SidebarLeft({groupList}) {
  const [showModal, setShowModal] = React.useState(false);

  return (
    <div className="sidebar-left">

      <div class="group-list-header">
        <h2>Group Chats</h2>
        <button className="join-group-button" title="Join Group" onClick= {() => setShowModal(true)}>
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
        {groupList.map((group, index) => (
          <Group
            key={index}
            groupName={group.groupName}
            groupPicSrc={group.groupPicSrc}
            lastMessage={group.lastMessage}
            timestamp={group.timestamp}
          />
        ))} 
      </div>
    </div>
  );
}

export default SidebarLeft;
