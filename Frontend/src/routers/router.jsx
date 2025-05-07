import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from '../App';
import Login from '../pages/Login';
import Chat from '../pages/Chat';

const isAuthenticated = () => {
  return !!localStorage.getItem('username');
};

const ProtectedRoute = ({ element }) => {
  return isAuthenticated() ? element : <Navigate to="/login" replace />;
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: '/',
        element: <Login onLogin={() => {}}/>,
      },
      {
        path: '/login',
        element: <Login />,
      },
      {
        path: '/chat',
        element: <ProtectedRoute element={<Chat />} />,
      },
      {
        path: '*',
        element: <Navigate to={isAuthenticated() ? '/chat' : '/login'} replace />,
      },
    ],
  },
]);

export default router;
