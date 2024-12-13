"use client";

import { useState, useEffect } from 'react';
import { refreshToken } from '@/app/api';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';
import config from '@/../config';

const API_URL = config.backendurl;
const LOGOUT_ENDPOINT = `${API_URL}token/logout/`;

interface JwtPayload {
  exp: number; // Expiration time as UNIX timestamp
  [key: string]: any;
}

const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [isTokenExpiring, setIsTokenExpiring] = useState<boolean>(false);
  const [timeLeft, setTimeLeft] = useState<number>(0);

  useEffect(() => {
    let tokenRefreshTimeout: NodeJS.Timeout | null = null;

    const checkToken = async () => {
      const accessToken = localStorage.getItem('access_token');

      if (accessToken) {
        try {
          const decoded: JwtPayload = jwtDecode(accessToken);
          const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
          const timeRemaining = decoded.exp - currentTime;
          setTimeLeft(timeRemaining);

          if (timeRemaining > 0) {
            setIsLoggedIn(true);

            if (timeRemaining < 60) {
              // Less than 60 seconds left
              setIsTokenExpiring(true);
              const success = await refreshToken();
              if (success) {
                setIsTokenExpiring(false);
                checkToken(); // Recheck after token refresh
              } else {
                console.warn('Token refresh failed. Logging out.');
                setIsLoggedIn(false);
                handleLogout();
              }
            } else {
              setIsTokenExpiring(false);

              // Set timeout to recheck the token 60 seconds before it expires
              if (tokenRefreshTimeout) clearTimeout(tokenRefreshTimeout);
              tokenRefreshTimeout = setTimeout(() => {
                checkToken();
              }, (timeRemaining - 60) * 1000);
            }
          } else {
            // Token has expired
            console.warn('Token has expired.');
            setIsLoggedIn(false);
            setIsTokenExpiring(false);
            setTimeLeft(0);
            handleLogout();
          }
        } catch (error) {
          console.error('Error decoding token:', error);
          setIsLoggedIn(false);
          setIsTokenExpiring(false);
          setTimeLeft(0);
          handleLogout();
        }
      } else {
        // No token found
        console.warn('No access token found.');
        setIsLoggedIn(false);
        setIsTokenExpiring(false);
        setTimeLeft(0);
      }
    };

    const handleLogout = () => {
      // Clear local storage and notify backend if needed
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      axios.post(LOGOUT_ENDPOINT).catch((error) => {
        console.error('Logout error:', error.message);
      });
    };

    // Initial check
    checkToken();

    // Listen for custom 'tokenUpdated' event
    const handleTokenUpdated = () => {
      checkToken();
    };

    window.addEventListener('tokenUpdated', handleTokenUpdated);

    // Cleanup on component unmount
    return () => {
      if (tokenRefreshTimeout) clearTimeout(tokenRefreshTimeout);
      window.removeEventListener('tokenUpdated', handleTokenUpdated);
    };
  }, []);

  return { isLoggedIn, isTokenExpiring, timeLeft };
};

export default useAuth;
