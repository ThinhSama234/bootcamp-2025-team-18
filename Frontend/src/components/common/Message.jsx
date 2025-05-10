import React from "react";
import "./Message.css";
import Avatar from "./Avatar";

function Message({ senderPic, senderName, content, isSent, timestamp, isPicture, onClick, id, onSelect, isSelected }) {


    if (!isSent) {
        return (
                <div className="message-container">
                    {!isSent && <Avatar src={ senderName === 'Gravel' ? '/Gravel.png' : senderPic} alt={senderName} size="small" />}
                    <div className="message-header">
                        <div className="sender-name">{senderName}</div>
                        <div title={timestamp} className={`message ${isSent ? "sent" : "received"}`}>
                            { isPicture ? <img src={content} className="message-image" onClick={ onClick } /> : content}
                        </div>
                    </div>
                    <input type="checkbox" className="message-checkbox-received" checked={isSelected} onChange={() => onSelect(id)} />
                </div>
            );
    } else {
        return (
            <div className="message-sent-container">
                <div className="message-sent-subcontainer">
                    <input type="checkbox" className="message-checkbox-sent" checked={isSelected} onChange={() => onSelect(id)}/>
                    <div title={timestamp} className="message sent">
                        {isPicture ? <img src={content} className="message-image" onClick={ onClick } /> : content}
                    </div>
                </div>
            </div>
        )
    }
}

export default Message;