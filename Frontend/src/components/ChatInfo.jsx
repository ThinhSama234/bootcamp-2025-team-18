import React from 'react';

function SidebarRight({groupName}) {
  return (
    <div className="sidebar-right">
      <img src="/group1.jpg" alt="Group" className="group-pic-large" />
      <h3>{groupName}</h3>

      <div className="member-list">
        <div className="member">
          <img src="/janedoe.jpg" alt="User" className="member-pic" />
          <span>Jane Doe</span>
        </div>
        <div className="member">
          <img src="/thisuser.jpg" alt="User" className="member-pic" />
          <span>This user</span>
        </div>
        {/* Repeat or map through member list */}
      </div>

      <div className="add-member-box">
        <input type="text" placeholder="Add new member..." />
        <button>Add</button>
      </div>
    </div>
  );
}

export default SidebarRight;
