import './Chat.css';
import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { SocketProvider } from '../context/SocketContext';
import { fetchGroupList } from '../api/groupService';
import SidebarLeft from '../components/GroupList';
import ChatWindow from '../components/MainChat';
import SidebarRight from '../components/ChatInfo';

function Chat() {

    const { username } = useAuth();

    const nullGroup = {
        groupName : 'Choose A Group',
        groupPicSrc: '/group1.jpg',
        members : [username]
    }
    const [groupList, setGroupList] = useState([]);
    const [selectedGroup, setSelectedGroup] = useState(nullGroup);
    const [loading, setLoading] = useState(true);

    const loadGroups = useCallback(async () => {
        if (!username) return;
        try {
            console.log(username);
            const groups = await fetchGroupList(username);
            setGroupList(groups);
            console.log(groups);
            if (groups.length > 0 && !selectedGroup) {
                setSelectedGroup(groups[0]);
            }
        } catch (err) {
            console.error("Failed to fetch groups:", err);
        } finally {
            setLoading(false);
        }
    }, [username, selectedGroup]);

    useEffect(() => {
        loadGroups();
    }, [loadGroups]);

    if (loading ) {
        return (
            <div className="loading-screen">
                <img src="/loading.gif" alt="Loading..." className="loading-gif" />
            </div>
        );
    }

    if (selectedGroup === null) {
        return (
            <SocketProvider username={username}>
                <div className="app-container">
                    <SidebarLeft 
                        groupList={groupList}
                        onGroupSelect={setSelectedGroup}
                        selectedGroupName = {selectedGroup === null ? '' : selectedGroup.groupName}
                        refreshGroupList = {loadGroups}
                    />
                    <ChatWindow group={selectedGroup} />
                    <SidebarRight group={selectedGroup} />
                </div>
            </SocketProvider>
        )
    }

    return (
        <SocketProvider username={username}>
            <div className="app-container">
                <SidebarLeft 
                    groupList={groupList}
                    onGroupSelect={setSelectedGroup}
                    selectedGroupName = {selectedGroup.groupName}
                    refreshGroupList = {loadGroups}
                />
                <ChatWindow group={selectedGroup} />
                <SidebarRight group={selectedGroup} />
            </div>
        </SocketProvider>
    );
}

export default Chat;
