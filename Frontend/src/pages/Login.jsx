import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import { useAuth } from '../context/AuthContext';

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = React.useState('Tuki');
  const [password, setPassword] = React.useState('123');
  const [error, setError] = React.useState('');

  const handleLogin = () => {
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.');
      return;
    }
  
    try {
      login(username);
      localStorage.setItem('username', username);
      navigate('/chat');
    } catch (error) {
      setError(error);
      alert('Error during login: ' + error.message);
    }
  };

  return (
    <div className="login-page">
      <div className="login-box">
        <h1 className="login-title">Gravel</h1>
        <h2 className="login-subtitle">Sign in</h2>
        <p className="login-instruction">Sign in with your username</p>
        <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => {setUsername(e.target.value); setError('');}}
        className="login-input"
        required
        />
        <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => {setPassword(e.target.value); setError('');}}
        className="login-input"
        required
        />
        <button className="login-button" onClick={ handleLogin }>Sign in</button>
      </div>
    </div>
  );
}

export default Login;
