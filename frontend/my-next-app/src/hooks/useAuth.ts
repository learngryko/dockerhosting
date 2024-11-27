"use client";

import { useState, useEffect } from 'react';
import { refreshToken } from '@/app/api';
import {jwtDecode} from 'jwt-decode';
import axios from 'axios';
import config from '@/../config'

const API_URL = config.backendurl;
const LOGOUT_ENDPOINT = `${API_URL}token/logout/`;


interface JwtPayload {
  exp: number;
  [key: string]: any;
}

const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [isTokenExpiring, setIsTokenExpiring] = useState<boolean>(false);
  const [timeLeft, setTimeLeft] = useState<number>(0);

  useEffect(() => {
    let tokenRefreshTimeout: NodeJS.Timeout;

    const checkToken = () => {
      const accessToken = localStorage.getItem('access_token');

      if (accessToken) {
        try {
          const decoded: JwtPayload = jwtDecode(accessToken);
          const currentTime = Date.now() / 1000; // Convert to seconds
          const expTime = decoded.exp;
          const timeRemaining = expTime - currentTime;

          setTimeLeft(timeRemaining);

          if (timeRemaining > 0) {
            setIsLoggedIn(true);

            if (timeRemaining < 60) { // Less than 60 seconds left
              setIsTokenExpiring(true);
              // Attempt to refresh the token
              refreshToken().then(success => {
                if (success) {
                  setIsTokenExpiring(false);
                  checkToken(); // Recheck the token after refreshing
                } else {
                  // Refresh failed, log out
                  setIsLoggedIn(false);
                }
              });
            } else {
              setIsTokenExpiring(false);
              // Set timeout to check the token again 60 seconds before it expires
              if (tokenRefreshTimeout) {
                clearTimeout(tokenRefreshTimeout);
              }
              tokenRefreshTimeout = setTimeout(() => {
                checkToken();
              }, (timeRemaining - 60) * 1000);
            }
          } else {
            // Token has expired
            setIsLoggedIn(false);
            setIsTokenExpiring(false);
            setTimeLeft(0);
          }
        } catch (error) {
          console.error('Error decoding token:', error);
          setIsLoggedIn(false);
          setIsTokenExpiring(false);
          setTimeLeft(0);
        }
      } else {
        // No token found
        setIsLoggedIn(false);
        setIsTokenExpiring(false);
        setTimeLeft(0);
      }
    };

    // Initial token check
    checkToken();

    // Listen for custom 'tokenUpdated' events to re-check the token
    const handleTokenUpdated = () => {
      checkToken();
    };

    window.addEventListener('tokenUpdated', handleTokenUpdated);

    // Cleanup on unmount
    return () => {
      if (tokenRefreshTimeout) {
        clearTimeout(tokenRefreshTimeout);
      }
      window.removeEventListener('tokenUpdated', handleTokenUpdated);
    };
  }, []);

  return { isLoggedIn, isTokenExpiring, timeLeft};
};

export default useAuth;
