import React from 'react';
import './Modal.css';

export function JoinGroupModal({ onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Join Group</h3>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>
        <p>Enter your group Id</p>
        <input
          type="text"
          className="group-id-input"
          placeholder="abc-def-ghi"
        />
        {/* TODO: SEND GROUP ID TO SERVER TO JOIN GROUP */}
        <button className="join-group-btn" onClick={ onClose }>Join Group</button>
      </div>
    </div>
  );
}

export function RenameGroupModal({ onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Rename Group</h3>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>
        <p>Enter new group name</p>
        <input
          type="text"
          className="group-id-input"
          placeholder="abc-def-ghi"
        />
        {/* TODO: SEND GROUP RENAME REQUEST TO SERVER */}
        <button className="join-group-btn" onClick={ onClose }>Rename Group</button>
      </div>
    </div>
  );
}

export function GroupPicModal({ onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Change Group Picture</h3>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>
        <p>Choose New Group Picture</p>
        <input
          type="file"
          accept="image/*"
          className="group-id-input"
        />
        {/* TODO: SEND GROUP RENAME REQUEST TO SERVER */}
        <button className="join-group-btn" onClick={ onClose }>Submit Change</button>
      </div>
    </div>
  );
}

export function AddUserModal({ onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Add User to Group</h3>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>
        <p>Enter new member's username</p>
        <input
          type="text"
          className="group-id-input"
          placeholder="user12345"
        />
        {/* TODO: SEND GROUP RENAME REQUEST TO SERVER */}
        <button className="join-group-btn" onClick={ onClose }>Add This User</button>
      </div>
    </div>
  );
}

export function ShareMediaModal({ onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Share A Picture</h3>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>
        <p>Choose A Picture</p>
        <input
          type="file"
          accept="image/*"
          className="group-id-input"
        />
        {/* TODO: SEND GROUP RENAME REQUEST TO SERVER */}
        <button className="join-group-btn" onClick={ onClose }>Send Picture</button>
      </div>
    </div>
  );
}