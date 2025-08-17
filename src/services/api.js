// api.js

import axios from 'axios';

// Detect if running in Electron
const isElectron = () =>
  typeof window !== 'undefined' &&
  window.api &&
  typeof window.api.getBackendUrl === 'function';

// Base URL (Electron → from preload, Browser → from env)
// Base URL (Electron → from preload, Browser → from env)
const API_BASE_URL = isElectron()
  ? window.api.getBackendUrl()
  : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:7000');

// Axios client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // increase to 60 seconds for heavier ops
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



export const submitComplianceTest = async (
  gameUrl,
  testType,
  selectedPolicy,
  selectedTestSuite,
  selectedTestCases
) => {
  try {
    console.log('calling the api');
    // make gameUrl available to detectService
    lastGameUrl = gameUrl;

    // Always call the unified /run-test endpoint using factory pattern
    const payload = {
      gameUrl,
      testType: testType || 'Regression',
      additionalParams: {
        selectedPolicy,
        selectedTestSuite,
        selectedTestCases,
      },
    };

    const res = await apiClient.post('/run-test', payload);

    console.log('api response received');

    const script = res?.data?.results?.script;
    if (script) {
      console.log("📜 Executing backend script from Regression service...");

      const executeScript = new Function(
        'isElectron',
        'detectService',
        'performClick',
        'window',
        `return (async () => { ${script} })();`
      );

      const detectServiceBound = async (testType, classID, image_data) =>
        await detectService(testType, classID, image_data);

      await executeScript(isElectron, detectServiceBound, performClick, window);

      console.log("✅ Script execution finished");
    }

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

//  test_execution_request = TestExecutionRequest(
//             game_url=str(request.gameUrl),
//             test_type=request.testType,
//             additional_params={
//                 "selectedPolicy": request.selectedPolicy,
//                 "selectedTestSuite": request.selectedTestSuite,
//                 "selectedTestCases": request.selectedTestCases,
//                 "class_ids":request.class_id,
//                 "image_data":request.imageData
//             }, 
//         )


let lastGameUrl = null;

const detectService = async (testType, classID, image_data) => {
  console.log(`Detecting service for type: ${testType}, classID: ${classID}`);
  try {
    const payload = {
      gameUrl: lastGameUrl,
      testType,
      additionalParams: {
        class_ids: Array.isArray(classID) ? classID : [classID],
        imageData: image_data,
      },
    };

    const res = await apiClient.post('/run-test', payload);
    // return only the data so the script can access response.results.*
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



export default apiClient;
