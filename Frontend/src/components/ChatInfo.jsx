import React from 'react';
import './ChatInfo.css'; // Assuming you have a CSS file for styling
import {GroupSettings, MemberList, SharedMedia} from './common/DropDown';

function SidebarRight({groupName}) {
  
  return (
    <div className="sidebar-right">
      <img src="/group1.jpg" alt="Group" className="group-pic-large" />
      <h3>{groupName}</h3>

      <GroupSettings header="Group Settings" />
      <MemberList members={[
        { name: 'Jane Doe', pic: '/janedoe.jpg' },
        { name: 'This user', pic: '/thisuser.jpg' },
        // Add more members as needed
      ]} />

      <SharedMedia mediaData={{
        April: [
          '/group1.jpg','/group1.jpg','/group1.jpg','/group1.jpg','/group1.jpg'
        ],
        March: [
          '/group1.jpg','/group1.jpg','/group1.jpg','/group1.jpg','/group1.jpg'
        ]
      }} />
    

      
    </div>
  );
}

export default SidebarRight;
