import React from 'react';
import './App.css';
import GroupList from './components/GroupList';
import MainChat from './components/MainChat';
import ChatInfo from './components/ChatInfo';

function App() {
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
