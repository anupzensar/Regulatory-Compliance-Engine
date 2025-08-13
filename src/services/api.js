// api.js

import axios from 'axios';

// Detect if running in Electron
const isElectron = () =>
  typeof window !== 'undefined' &&
  window.api &&
  typeof window.api.getBackendUrl === 'function';

// Base URL (Electron → from preload, Browser → from env)
const API_BASE_URL = isElectron()
  ? window.api.getBackendUrl()
  : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:7000');

// Axios client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`📡 ${config.method?.toUpperCase()} → ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response logging
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Check backend status
 * - Electron → calls preload's checkBackendStatus
 * - Browser → GET /
 */
export const checkBackendStatus = async () => {
  if (isElectron()) {
    try {
      return await window.api.checkBackendStatus();
    } catch (err) {
      console.error('Electron backend check failed:', err);
      throw err;
    }
  } else {
    try {
      const res = await apiClient.get('/');
      return res.data;
    } catch (err) {
      throw new Error('Backend not accessible: ' + err.message);
    }
  }
};

/**
 * Perform click
 * - Electron → calls preload's performClick
 * - Browser → No-op (could add browser-side simulation)
 */
export const performClick = async (classId, x, y) => {
  if (isElectron()) {
    return await window.api.performClick(classId, x, y);
  } else {
    console.warn('performClick called in browser — no-op');
    return { success: false, reason: 'Not running in Electron' };
  }
};

/**
 * Submit Compliance Test
 */
export const submitComplianceTest = async (
  gameUrl,
  testType,
  selectedPolicy,
  selectedTestSuite,
  selectedTestCases
) => {
  try {
    const res = await apiClient.post('/run-test', {
      gameUrl,
      testType,
      selectedPolicy,
      selectedTestSuite,
      selectedTestCases,
    });

    run_test(res.data.test_flow);

    return res.data;
  } catch (error) {
    if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Invalid request');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Try later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout.');
    } else {
      throw new Error('Network error.');
    }
  }
};




/**
 * Dummy test runner (replace with real logic)
 */
const run_test = (testData) => {
  let image_data = null;
  let x, y;
  const dummyTestCase = [
    { id: 1, step: 'captureSS', params: null },
    { id: 2, step: 'detectService', params: { testType: 'UI Element Detection', classID: 0 } },
    { id: 3, step: 'clickService' },
    { id: 4, step: 'captureSS', params: null },
    { id: 5, step: 'detectService', params: { testType: 'UI Element Detection', classID: 1 } },
    { id: 6, step: 'clickService' },
  ];

  for (const testCase of dummyTestCase) {
    console.log(`▶ Step ${testCase.id}: ${testCase.step}`, testCase.params || '');

    if (testCase.step === 'captureSS') {
      if (isElectron()) {
        image_data = window.api.captureScreenshot();
      } else {
        console.log('(Browser) Screenshot capture placeholder');
      }
    } else if (testCase.step === 'detectService') {
      console.log(`Detecting service: ${testCase.params.testType}`);
      // TODO: Implement detection logic here
      testType = "UI Element Detection";
      let response = detectService(testType, testCase.params.classID, image_data);
      x = response.x || 0;
      y = response.y || 0;
      console.log(`Detected service at (${x}, ${y})`);
      console.log(`Detected service response:`, response);

    } else if (testCase.step === 'clickService') {
      performClick(testCase.params.classID || 0, x, y);
    }
  }
};

const detectService = async (testType, classID, image_data) => {
  // Placeholder for service detection logic
  console.log(`Detecting service for type: ${testType}, classID: ${classID}`);
  try {
    const res = await apiClient.post('/run-test', {
      gameUrl,
      testType,
      selectedPolicy,
      selectedTestSuite,
      selectedTestCases,
      class_id: classID,
      imageData: image_data,
    });

  } catch (error) {
    if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Invalid request');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Try later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout.');
    } else {
      throw new Error('Network error.');
    }
  }

  return { success: true, message: 'Service detected successfully' };
};




export default apiClient;
