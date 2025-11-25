import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        if (parsed.token) {
          config.headers.Authorization = `Bearer ${parsed.token}`;
        }
      } catch (e) {
        // Ignore parsing errors
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const config = error.config || {};
    const isSilent = config.silent === true;
    const status = error.response?.status;
    
    // Handle 401 - unauthorized
    if (status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    // Suppress console errors for expected failures (404, 400) if marked as silent
    // Note: Browser network errors will still show in Network tab, but won't clutter Console
    if (isSilent && (status === 404 || status === 400)) {
      // Return a rejected promise without logging
      return Promise.reject(error);
    }
    
    return Promise.reject(error);
  }
);

export default api;

