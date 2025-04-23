import React from 'react';
import './App.css';
import GroupList from './components/GroupList';
import MainChat from './components/MainChat';
import ChatInfo from './components/ChatInfo';



function App() {
  // TODO: Fetch group list from the backend server
  const groupList = [
    "Paris Trip Planning",
    "Japan Adventure Crew",
    "Roadtrip USA",
    "Bali Escape Group",
    "Iceland Expedition Team",
    "Italy Food Tour Squad",
    "Thailand Backpackers",
    "Australia Outback Journey",
    "Greece Island Hoppers",
    "Morocco Desert Dreamers"
  ];
  const groupName = "Travel Planning Group";
  
  return (
    <div className="app-container">
      <GroupList groupName={groupName} />
      <MainChat groupName={groupName} />
      <ChatInfo groupName={groupName} />
    </div>
  );
}

export default App;
