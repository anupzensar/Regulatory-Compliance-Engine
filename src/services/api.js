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

// ----------------- EDIT: centralized error handler -----------------
function handleApiError(error) {
  if (error.response?.status === 400) {
    throw new Error(error.response.data.detail || 'Invalid request');
  } else if (error.response?.status >= 500) {
    throw new Error('Server error. Please try again later.');
  } else if (error.code === 'ECONNABORTED') {
    throw new Error('Request timeout. Please check your connection.');
  } else if (error.response) {
    // other HTTP errors
    throw new Error(error.response.data?.detail || `Request failed with status ${error.response.status}`);
  } else {
    throw new Error('Network error. Please check your connection.');
  }
}
// ------------------------------------------------------------------

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

// Response interceptor for logging (but error shaping is done in wrapper)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ----------------- EDIT: new semantic wrappers -----------------

/**
 * Starts a regression (or compliance) test.
 * Returns backend payload: expected to contain test_id and next_step.
 */
export const startRegressionTest = async (gameUrl) => {
  try {
    const response = await apiClient.post('/run-test', {
      gameUrl,
      testType: 'Regression',
    });
    return response.data; // { test_id, next_step, ... }
  } catch (err) {
    handleApiError(err);
  }
};

/**
 * Submits a single step of the test flow.
 * Expects:
 *  - test_id: string
 *  - class_id: number
 *  - screenshot: string (data URI)
 *  - action_result: object (e.g., { clicked: boolean, ... })
 */
export const submitTestStep = async ({ test_id, class_id, screenshot, action_result }) => {
  try {
    const response = await apiClient.post('/run-test-step', {
      test_id,
      class_id,
      screenshot,
      action_result,
    });
    return response.data; // contains step_result, next_step or final result
  } catch (err) {
    handleApiError(err);
  }
};

// ----------------- EDIT: preserve / adapt legacy function -----------------
export const submitComplianceTest = async (gameUrl, testType) => {
  try {
    const response = await apiClient.post('/run-test', {
      gameUrl,
      testType,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export default apiClient;
