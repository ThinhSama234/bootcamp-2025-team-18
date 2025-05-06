import React from 'react';
import { useNavigate } from 'react-router-dom';

function Login({ onLogin }) {
  const navigate = useNavigate();

  const handleLogin = () => {
    onLogin();            // Update authentication state
    navigate('/chat');    // Navigate to chat after login
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <button onClick={handleLogin}>Log In</button>
    </div>
  );
}

export default Login;
