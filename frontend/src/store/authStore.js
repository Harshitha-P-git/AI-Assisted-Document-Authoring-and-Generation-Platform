import { create } from 'zustand';
import api from '../services/api';

const useAuthStore = create((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  login: async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      const { access_token } = response.data;
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user info
      const userResponse = await api.get('/auth/me');
      
      const state = {
        token: access_token,
        user: userResponse.data,
        isAuthenticated: true,
      };
      
      set(state);
      
      // Persist to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth-storage', JSON.stringify(state));
      }
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  },
  
  register: async (userData) => {
    try {
      await api.post('/auth/register', userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  },
  
  logout: () => {
    delete api.defaults.headers.common['Authorization'];
    const state = {
      user: null,
      token: null,
      isAuthenticated: false,
    };
    set(state);
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-storage');
    }
  },
  
  initializeAuth: () => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('auth-storage');
      if (stored) {
        try {
          const state = JSON.parse(stored);
          if (state.token) {
            api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
            set(state);
          }
        } catch (e) {
          localStorage.removeItem('auth-storage');
        }
      }
    }
  },
}));

// Initialize auth on load
if (typeof window !== 'undefined') {
  useAuthStore.getState().initializeAuth();
}

export default useAuthStore;

