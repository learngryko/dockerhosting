import axios, { AxiosResponse } from 'axios';
import config from '../../config'

interface LoginResponse {
  access: string;
  refresh: string;
}

interface LoginPayload {
  username: string;
  password: string;
}

const API_URL = config.backendurl;
const LOGIN_ENDPOINT = `${API_URL}token/`;
const REFRESH_ENDPOINT = `${API_URL}token/refresh/`;

export async function login(username: string, password: string): Promise<boolean> {
  try {
    const response: AxiosResponse<LoginResponse> = await axios.post(
      LOGIN_ENDPOINT, 
      { username, password },
      { withCredentials: true } // Allows sending cookies in cross-origin requests
    );
    const { access, refresh } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

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
