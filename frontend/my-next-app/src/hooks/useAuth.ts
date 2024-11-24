import { useState, useEffect } from 'react';
import { refreshToken } from '@/app/api'
import { jwtDecode } from 'jwt-decode';


const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [isTokenExpiring, setIsTokenExpiring] = useState<boolean>(false);
  const [timeLeft, setTimeLeft] = useState<number>(0); // Track time left for token expiration
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null);

  // Decode token and get the expiration time
  const getTokenExpiry = (token: string) => {
    const decoded: any = jwtDecode(token);
    return decoded.exp * 1000; // Convert to milliseconds
  };

  // Function to check if the token is about to expire and refresh it
  const checkTokenExpiry = () => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      const expiryTime = getTokenExpiry(accessToken);
      const timeLeft = expiryTime - Date.now();

      if (timeLeft <= 5 * 60 * 1000 && timeLeft > 0) { // If expiry time is less than 5 minutes
        setIsTokenExpiring(true);
        if (timer) clearTimeout(timer);

        setTimer(
          setTimeout(async () => {
            const success = await refreshToken(); // Attempt to refresh the token
            if (!success) {
              setIsLoggedIn(false);
            }
            setIsTokenExpiring(false);
            setTimeLeft(0);
          }, timeLeft)
        );
      } else if (timeLeft > 0) {
        setTimeLeft(timeLeft);
      }
    }
  };

  // Check login status and set up token expiry check
  useEffect(() => {
    const checkLoginStatus = () => {
      const accessToken = localStorage.getItem('access_token');
      setIsLoggedIn(!!accessToken);
      if (accessToken) {
        checkTokenExpiry(); // Check token expiry when user is logged in
      }
    };

    checkLoginStatus();
    window.addEventListener('storage', checkLoginStatus); // Listen for localStorage changes

    return () => {
      window.removeEventListener('storage', checkLoginStatus); // Cleanup listener
      if (timer) clearTimeout(timer); // Cleanup timer
    };
  }, [timer]);

  return { isLoggedIn, isTokenExpiring, timeLeft };
};

export default useAuth;
