import React from 'react';

function SidebarLeft({groupName}) {
  return (
    <div className="sidebar-left">
      <h2>Groups</h2>
      <div className="group" style={{backgroundColor: '#e4e6eb'}}>
        <img src="/group1.jpg" alt="Group" className="group-pic" />
        <div className="group-info">
          <h4>{groupName}</h4>
          <p>Last message here...</p>
        </div>
      </div>
      <div className="group">
        <img src="/group1.jpg" alt="Group" className="group-pic" />
        <div className="group-info">
          <h4>Another Travel Planning Group</h4>
          <p>Last message here...</p>
        </div>
      </div>
      {/* You can map through your group list here */}
    </div>
  );
}

export default SidebarLeft;
