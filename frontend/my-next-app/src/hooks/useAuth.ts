// hooks/useAuth.ts

import { useState, useEffect } from 'react';

const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  useEffect(() => {
    const checkLoginStatus = () => {
      const accessToken = localStorage.getItem('access_token');
      setIsLoggedIn(!!accessToken);
    };

    checkLoginStatus();
    window.addEventListener('storage', checkLoginStatus); // Listen for localStorage changes

    return () => window.removeEventListener('storage', checkLoginStatus); // Cleanup listener
  }, []);

  return isLoggedIn;
};

export default useAuth;
