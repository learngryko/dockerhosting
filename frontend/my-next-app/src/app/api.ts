import axios, { AxiosResponse } from 'axios';
import config from '../../config';

interface LoginResponse {
  access: string;
  refresh: string;
}

const API_URL = config.backendurl;
const LOGIN_ENDPOINT = `${API_URL}token/`;
const REFRESH_ENDPOINT = `${API_URL}token/refresh/`;
const LOGOUT_ENDPOINT = `${API_URL}token/logout/`; // Django logout endpoint

// Login function
export async function login(username: string, password: string): Promise<boolean> {
  try {
    const response: AxiosResponse<LoginResponse> = await axios.post(
      LOGIN_ENDPOINT,
      { username, password },
      { withCredentials: true } // Allows sending cookies in cross-origin requests
    );
    const { access, refresh } = response.data;

    // Set tokens in localStorage
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    // Dispatch a custom event
    window.dispatchEvent(new Event('tokenUpdated'));

    return true;
  } catch (error: any) {
    if (error.response) {
      console.error('Login failed:', error.response.data || error.message);
    } else {
      console.error('Login failed:', error.message);
    }
    return false;
  }
}

// Refresh token function
export async function refreshToken(): Promise<boolean> {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) {
    console.error('No refresh token found.');
    return false;
  }

  try {
    const response: AxiosResponse<LoginResponse> = await axios.post(
      REFRESH_ENDPOINT,
      { refresh },
      { withCredentials: true } // Ensures cookies are included for cross-origin requests
    );
    const { access } = response.data;
    localStorage.setItem('access_token', access);
    return true;
  } catch (error: any) {
    if (error.response) {
      console.error('Error refreshing token:', error.response.data || error.message);
    } else {
      console.error('Error refreshing token:', error.message);
    }
    return false;
  }
}

// Logout function
export async function logout(): Promise<boolean> {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    const accessToken = localStorage.getItem('access_token'); // Get the access token

    if (refreshToken && accessToken) {
      // Notify Django backend to blacklist the token
      await axios.post(
        LOGOUT_ENDPOINT,
        { refresh: refreshToken },
        {
          withCredentials: true, // Include cookies if necessary
          headers: {
            Authorization: `Bearer ${accessToken}`, // Add Authorization header
          },
        }
      );
    }

    // Clear tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Dispatch a custom event
    window.dispatchEvent(new Event('tokenCleared'));

    return true;
  } catch (error: any) {
    console.error('Error logging out:', error.message);
    return false;
  }
}

