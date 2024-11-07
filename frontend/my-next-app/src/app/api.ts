import axios, { AxiosResponse } from 'axios';
import * as dotenv from 'dotenv';
dotenv.config();


// Define the structure of the response you expect from the login API
interface LoginResponse {
  access: string;
  refresh: string;
}

// Define the payload for login request
interface LoginPayload {
  username: string;
  password: string;
}

const API_URL = process.env.API_URL || 'http://django:8000/api/';


// Login function with types
export async function login(username: string, password: string): Promise<boolean> {
  try {
    const response: AxiosResponse<LoginResponse> = await axios.post(API_URL, {
      username,
      password,
    });
    const { access, refresh } = response.data;

    // Store tokens (you can store them in localStorage or cookies)
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    return true;
  } catch (error: any) {  // `error` is typed as `any` to access its properties
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
      'http://your-django-api-url/api/token/refresh/',
      { refresh }
    );
    const { access } = response.data;
    localStorage.setItem('access_token', access);
    return true;
  } catch (error: any) {  // `error` is typed as `any` to access its properties
    if (error.response) {
      console.error('Error refreshing token:', error.response.data || error.message);
    } else {
      console.error('Error refreshing token:', error.message);
    }
    return false;
  }
}
