import React from 'react';
import './MainChat.css'; 
import Avatar from './common/Avatar';
import Message from './common/Message';
import { ShareMediaModal } from './common/Modal';

function ChatWindow({groupName, groupPicSrc}) {
  const [showShareMediaModal, setShareMediaModal] = React.useState(false);

  return (
    <div className="main-chat">

      <div className="chat-header">
        <div className="chat-header-group-info">
          <Avatar src={groupPicSrc} alt="Group Pic" size="large"/>
          <h3>{groupName}</h3>
        </div>
        <button className="chat-header-button" title="Group Info" onClick={() => alert('Group Info')}>
          <img src="/group-info-icon.png" alt="Info" className="info-icon" />
        </button>
      </div>
      
      <div className="chat-messages">
        <Message content="Nice to be here!" isSent={true} />
        <Message content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam ligula nibh, porta id gravida ac, euismod sed odio. Morbi ut." isSent={true} />
        <Message senderPic="/janedoe.jpg" senderName="John Doe" content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum dapibus sem rutrum aliquet vehicula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla et dapibus leo. Nulla at mollis velit. Etiam finibus id mi eget fringilla. Nulla rutrum venenatis leo non dapibus. Sed justo nunc, suscipit eu posuere vitae, tempus ut risus." isSent={false} />
        <Message senderPic="/janedoe.jpg" senderName="John Doe" content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam ligula nibh, porta id gravida ac, euismod sed odio. Morbi ut." isSent={false} />
        <Message senderPic="/janedoe.jpg" senderName="John Doe" content="Hi everyone!" isSent={false} />
      </div>
      
      <div className="chat-input">
        <button className='request-button' title='Request Recommend' onClick={() => alert('Request Recommend')}>
          <img src='/request-icon.png' alt='Request icon' className='request-icon' />
        </button>
        <button className='add-media-button' title='Add Media' onClick={() => setShareMediaModal(true)}>
          <img src='/media-icon.png' alt='Add media icon' className='add-media-icon' />
        </button>
        <input type="text" placeholder="Type a message..." />
        <button className='send-button' title='Send' onClick={() => alert('Message sent')}>
          <img src='/send-icon.png' alt='Send icon' className='send-icon' />
        </button>
      </div>
      {showShareMediaModal && <ShareMediaModal onClose={() => setShareMediaModal(false)} />}
    </div>
  );
}

export default ChatWindow;
