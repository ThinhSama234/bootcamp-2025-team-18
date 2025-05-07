import React, { useEffect } from 'react';
import './ChatInfo.css'; // Assuming you have a CSS file for styling
import {GroupSettings, MemberList, SharedMedia} from './common/DropDown';

function SidebarRight({group}) {
  const [loading, setLoading] = React.useState(true);
  const [groupMembers, setGroupMembers] = React.useState(null);

  useEffect(() => {
    if (!group) return; 

    const getGroupDetails = async () => {
      try {
        setGroupMembers(group.members.map((member) => {
          return {
            name: member,
            pic: 'thisuser.jpg' // Fallback to default image if not available
          };
        }));
        console.log("Group members:", groupMembers);
      } catch (err) {
        console.error("Failed to fetch group details:", err);
      } finally {
        setLoading(false);
      }
    };

    getGroupDetails();
  } , [group]);
  
  if (loading || !group) {
    return (
      <div className="loading-screen">
        <img src="/loading.gif" alt="Loading..." className="loading-gif" />
      </div>
    );
  }

  return (
    <div className="sidebar-right">
      <img src="/group1.jpg" alt="Group" className="group-pic-large" />
      <h3>{group.groupName}</h3>

      <GroupSettings header="Group Settings" />
      {
        groupMembers && <MemberList members={groupMembers} />
      }

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
