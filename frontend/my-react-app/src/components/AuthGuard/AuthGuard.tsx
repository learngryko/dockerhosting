// src/components/AuthGuard.tsx

import React from 'react';
import { Navigate } from 'react-router-dom';

interface AuthGuardProps {
  children: React.ReactNode;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem('access_token');

  return isAuthenticated ? <>{children}</> : <Navigate to="/" />;
};

export default AuthGuard;
