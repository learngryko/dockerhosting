// src/services/api.ts

import axios from 'axios';

// Set up the base API instance
const api = axios.create({
  baseURL: 'http://django:8000/api',  // Adjust to your backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the token to each request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Handle token refreshing if access token expires
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      try {
        const response = await axios.post('http://django:8000/api/token/refresh/', {
          refresh: refreshToken,
        });
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        api.defaults.headers['Authorization'] = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        console.log("Refresh token expired or invalid, logging out.");
        localStorage.clear();  // Clear tokens on failed refresh
        window.location.href = '/';  // Redirect to login
      }
    }
    return Promise.reject(error);
  }
);

export default api;
