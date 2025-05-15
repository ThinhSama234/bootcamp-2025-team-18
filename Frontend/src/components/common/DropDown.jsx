import React, { useState } from 'react';
import './DropDown.css';
import { GroupPicModal, RenameGroupModal, AddUserModal } from './Modal';

export function GroupSettings({header}) {
  const [isOpen, setIsOpen] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [showGroupPicModal, setShowGroupPicModal] = useState(false);

  return (
    <div className="dropdown-container">
      <div className="dropdown-header" onClick={() => setIsOpen(!isOpen)}>
        {header} {isOpen ? '▲' : '▼'}
      </div>
      {isOpen && (
        <div className="dropdown-content">
          <button className="dropdown-item" onClick={() => setShowRenameModal(true)}>
            <img src="rename-icon.png" alt="Rename" className="icon" />
            <p>Change group name</p>
          </button>
          <button className="dropdown-item" onClick={() => setShowGroupPicModal(true)}>
            <img src="change-pic-icon.png" alt="Rename" className="icon" />
            <p>Change group picture</p>
          </button>
        </div>
      )}
      {showRenameModal && <RenameGroupModal onClose={() => setShowRenameModal(false)} />}
      {showGroupPicModal && <GroupPicModal onClose={() => setShowGroupPicModal(false)} />}
    </div>

    
  );
}

export function MemberList({ members, onAddUser }) {
  const [isOpen, setIsOpen] = useState(false);
  const [showAddUserModal, setShowAddUserModal] = useState(false);

  return (
    <div className="dropdown-container">
      <div className="dropdown-header" onClick={() => setIsOpen(!isOpen)}>
        Members {isOpen ? '▲' : '▼'}
      </div>
      {isOpen && (
        <div className="dropdown-content">
                {members.map((member, index) => (
                  <button className="dropdown-item" key={index}>
                    <img src={member.pic} alt={member.name} className="member-pic" />
                    <p>{member.name}</p>
                  </button>
                ))}
                <button className="dropdown-item" onClick={() => setShowAddUserModal(true)}>
                  <img src="add-user-icon.png" alt="Add User" className="icon" />
                  <p>Add User</p>
                </button>
        </div>
      )}
      {showAddUserModal && <AddUserModal onClose={() => setShowAddUserModal(false)} onAddUser={onAddUser}/>}
    </div>
  );
}

export function SharedMedia({mediaData}) {
  const [isOpen, setIsOpen] = useState(false);
  const [zoomedImg, setZoomedImg] = useState(null);

  const handleImageClick = (src) => {
    setZoomedImg(src);
  };

  const closeModal = () => {
    setZoomedImg(null);
  };

  return (
    <div className="dropdown-container">
      <div className="dropdown-header" onClick={() => setIsOpen(!isOpen)}>
        Shared Media {isOpen ? '▲' : '▼'}
      </div>
      
      {isOpen && (
        <div className="media-content">
          {Object.keys(mediaData).map(month => (
            <div key={month} className="media-month-section">
              <h4>{month}</h4>
              <div className="media-grid">
                {mediaData[month].map((src, index) => (
                  <img
                    key={index}
                    src={src}
                    alt="Shared"
                    className="media-img"
                    onClick={() => handleImageClick(src)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {zoomedImg && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content">
            <img src={zoomedImg} alt="Zoomed" />
          </div>
        </div>
      )}
    </div>
  );
}
