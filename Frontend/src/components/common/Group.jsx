import React from "react";
import "./Group.css";
import Avatar from "./Avatar";

function Group({ groupName, groupPicSrc, lastMessage, timestamp }) {
    return (
        <div className="group">
            <Avatar src={groupPicSrc} alt="Group" size="large" />
            <div className="group-info">
                <h4>{groupName}</h4>
                <div className="message-info">
                    <div className="last-message-container">
                        <p>{lastMessage}</p>
                    </div>
                    <span className="timestamp">{timestamp}</span>
                </div>
            </div>
        </div>
    );
}
    

export default Group;    