import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import GroupList from './components/GroupList';
import MainChat from './components/MainChat';
import ChatInfo from './components/ChatInfo';
import Login from './components/Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  
  const groupList = [
    {
      groupName: "Paris Trip Planning",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Eiffel Tower tickets booked!",
      timestamp: "1h ago"
    },
    {
      groupName: "Japan Adventure Crew",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Cherry blossoms soon 🌸",
      timestamp: "3h ago"
    },
    {
      groupName: "Roadtrip USA",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Next stop: Grand Canyon!",
      timestamp: "Yesterday"
    },
    {
      groupName: "Bali Escape Group",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Book the beachfront villa?",
      timestamp: "4d ago"
    },
    {
      groupName: "Iceland Expedition Team",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Northern lights alert!",
      timestamp: "2d ago"
    },
    {
      groupName: "Italy Food Tour Squad",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Who's up for gelato?",
      timestamp: "5h ago"
    },
    {
      groupName: "Thailand Backpackers",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Don't forget bug spray!",
      timestamp: "1w ago"
    },
    {
      groupName: "Australia Outback Journey",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Watch out for kangaroos 🦘",
      timestamp: "3d ago"
    },
    {
      groupName: "Greece Island Hoppers",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Santorini sunsets, anyone?",
      timestamp: "6h ago"
    },
    {
      groupName: "Morocco Desert Dreamers",
      groupPicSrc: "/group1.jpg",
      lastMessage: "Camel tour confirmed!",
      timestamp: "10m ago"
    }
  ];
  
  return (
    <Router>
    <Routes>
      <Route
        path="/login"
        element={<Login onLogin={() => setIsAuthenticated(true)} />}
      />
      <Route
        path="/chat"
        element={
          isAuthenticated ? (
            <div className="app-container">
    <GroupList groupList={groupList} />
    <MainChat groupName={groupList[0].groupName} groupPicSrc={groupList[0].groupPicSrc}/>
    <ChatInfo groupName={groupList[0].groupName} />
  </div> 
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? "/chat" : "/login"} replace />}
      />
    </Routes>
  </Router>
  );
}

export default App;
