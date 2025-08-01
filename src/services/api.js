// API configuration
// Check if running in Electron environment
const isElectron = () => {
  return typeof window !== 'undefined' && window.api && window.api.getBackendUrl;
};

const API_BASE_URL = isElectron() 
  ? window.api.getBackendUrl() 
  : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:7000');

// API client with proper error handling
import axios from 'axios';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API functions

// Check backend status (useful for Electron)
export const checkBackendStatus = async () => {
  try {
    const response = await apiClient.get('/');
    return response.data;
  } catch (error) {
    console.error('Backend not available:', error.message);
    throw new Error('Backend server is not running or not accessible');
  }
};

export const submitComplianceTest = async (gameUrl, testType) => {
  try {
    const response = await apiClient.post('/run-test', {
      gameUrl,
      testType,
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Invalid request');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.');
    } else {
      throw new Error('Network error. Please check your connection.');
    }
  }
};

export const launchRegression = async (url, headless = true) => {
  const response = await axios.get('http://localhost:7000/get-regression', {
    url,
    headless,
  });
  return response.data;
};

export default apiClient;
