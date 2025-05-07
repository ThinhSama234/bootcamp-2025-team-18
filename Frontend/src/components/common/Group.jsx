import React from "react";
import "./Group.css";
import Avatar from "./Avatar";

function Group({ groupName, groupPicSrc, lastMessage, timestamp, onClick, isSelected }) {
    return (
        <div className={`group ${isSelected ? 'selected' : ''}`} onClick={onClick}>
            <Avatar src={groupPicSrc} alt="Group" size="large" />
            <div className="group-info">
                <h4>{groupName}</h4>
                <div className="message-info">
                    <div className="last-message-container">
                        <p>{lastMessage ? lastMessage : "No message"}</p>
                    </div>
                    <span className="timestamp">{timestamp !== "NaNw ago" ? timestamp : ""}</span>
                </div>
            </div>
        </div>
    );
}
    

export default Group;    