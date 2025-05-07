import React from "react";
import "./Message.css";
import Avatar from "./Avatar";

function Message({ senderPic, senderName, content, isSent }) {
    if (!isSent) {
        return (
                <div className="message-container">
                    {!isSent && <Avatar src={senderPic} alt={senderName} size="small" />}
                    <div className="message-header">
                        <div className="sender-name">{senderName}</div>
                        <div className={`message ${isSent ? "sent" : "received"}`}>
                            {content}
                        </div>
                    </div>
                    <input type="checkbox" className="message-checkbox-received" />
                </div>
            );
    } else {
        return (
            <div className="message-sent-container">
                <div className="message-sent-subcontainer">
                    <input type="checkbox" className="message-checkbox-sent" />
                    <div className="message sent">
                        {content}
                    </div>
                </div>
            </div>
        )
    }
}

export default Message;