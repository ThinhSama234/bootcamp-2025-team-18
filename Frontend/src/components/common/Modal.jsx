import React, { useState } from 'react';
import './Modal.css';
import { createGroup } from '../../api/groupService';
import { useSocket } from '../../context/SocketContext';

export function JoinGroupModal({ onClose }) {
  const [mode, setMode] = useState('create'); // 'create' or 'join'
  const [groupName, setGroupName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { joinGroup, socket } = useSocket();

  const username = localStorage.getItem('username');

  const handleSubmit = async () => {
    if (!groupName.trim()) {
      setError('Group name cannot be empty.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (mode === 'create') {
        await createGroup(groupName.trim(), username);
      } else {
        joinGroup(groupName.trim());
      }
      onClose();
    } catch (err) {
      console.error(`Failed to ${mode} group:`, err);
      setError(`Failed to ${mode} group. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <h3>{mode === 'create' ? 'Create New Group' : 'Join Existing Group'}</h3>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>

        <div className="toggle-container">
          <label>
            <input
              type="radio"
              name="groupMode"
              value="create"
              checked={mode === 'create'}
              onChange={() => setMode('create')}
            />
            Create
          </label>
          <label>
            <input
              type="radio"
              name="groupMode"
              value="join"
              checked={mode === 'join'}
              onChange={() => setMode('join')}
            />
            Join
          </label>
        </div>

        <input
          type="text"
          className="group-id-input"
          placeholder="Enter group name"
          value={groupName}
          onChange={e => setGroupName(e.target.value)}
        />

        {error && <p className="error-text">{error}</p>}

        <button className="join-group-btn" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Processing...' : mode === 'create' ? 'Create Group' : 'Join Group'}
        </button>
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