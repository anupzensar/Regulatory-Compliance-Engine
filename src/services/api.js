// filepath: api.js
import axios from 'axios';

// Detect if running in Electron
const isElectron = () =>
  typeof window !== 'undefined' &&
  window.api &&
  typeof window.api.getBackendUrl === 'function';

// Base URL (Electron → from preload, Browser → from env)
const API_BASE_URL = isElectron()
  ? window.api.getBackendUrl()
  : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:7000');

// Axios client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s for heavier ops
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
 * Perform click (Electron only)
 */
export const performClick = async (classId, x, y) => {
  if (isElectron()) {
    const xi = Number.isFinite(Number(x)) ? Math.round(Number(x)) : null;
    const yi = Number.isFinite(Number(y)) ? Math.round(Number(y)) : null;
    if (xi == null || yi == null) {
      console.warn('performClick skipped: invalid coordinates', x, y);
      return { success: false, reason: 'Invalid coordinates' };
    }
    return await window.api.performClick(classId, xi, yi);
  } else {
    console.warn('performClick called in browser — no-op');
    return { success: false, reason: 'Not running in Electron' };
  }
};

// Keep last used URL for per-step calls
let lastGameUrl = null;

/**
 * Main compliance test executor
 */
export const submitComplianceTest = async (
  gameUrl,
  testType,
  selectedPolicy,
  selectedTestSuite,
  selectedTestCases
) => {
  try {
    console.log('calling the api');
    lastGameUrl = gameUrl;

    const payload = {
      gameUrl,
      testType,
      selectedPolicy: selectedPolicy ?? null,
      selectedTestSuite: selectedTestSuite ?? null,
      selectedTestCases: selectedTestCases ?? null,
      additionalParams: {},
    };
    console.log('payload:', payload);

    const res = await apiClient.post('/run-test', payload);

    console.log('api response received');
    console.log('Response data:', res.data);

    if (res.data.script) {
      console.log('📜 Executing backend script...');

      const logs = [];
      const steps = [];

      const originalLog = console.log;
      const originalWarn = console.warn;
      const originalError = console.error;

      try {
        console.log = (...args) => {
          logs.push(args.map(String).join(' '));
          originalLog(...args);
        };
        console.warn = (...args) => {
          logs.push('[WARN] ' + args.map(String).join(' '));
          originalWarn(...args);
        };
        console.error = (...args) => {
          logs.push('[ERROR] ' + args.map(String).join(' '));
          originalError(...args);
        };

        const recordStep = async (classId, x, y) => {
          try {
            if (isElectron() && window.api?.captureScreenshot) {
              const b64 = await window.api.captureScreenshot();
              steps.push({
                step_index: steps.length + 1,
                class_id: classId,
                x,
                y,
                imageData: `data:image/png;base64,${b64}`,
                timestamp: new Date().toISOString(),
              });
            } else {
              steps.push({
                step_index: steps.length + 1,
                class_id: classId,
                x,
                y,
                imageData: null,
                timestamp: new Date().toISOString(),
              });
            }
          } catch (e) {
            logs.push('[recordStep error] ' + String(e?.message || e));
          }
        };

        const recordImageStep = async (operation, details = {}) => {
          try {
            if (isElectron() && window.api?.captureScreenshot) {
              const b64 = await window.api.captureScreenshot();
              steps.push({
                step_index: steps.length + 1,
                operation,
                details,
                imageData: `data:image/png;base64,${b64}`,
                timestamp: new Date().toISOString(),
              });
            } else {
              steps.push({
                step_index: steps.length + 1,
                operation,
                details,
                imageData: null,
                timestamp: new Date().toISOString(),
              });
            }
          } catch (e) {
            logs.push('[recordImageStep error] ' + String(e?.message || e));
          }
        };

        const wrappedPerformClick = async (classId, x, y) => {
          await recordStep(classId, x, y);
          return await performClick(classId, x, y);
        };

        const wrappedFindTextInImage = async (imageData, text) => {
          await recordImageStep('OCR', { text, imageData: imageData ? 'provided' : 'captured' });
          return await findTextInImage(imageData, text);
        };

        const wrappedCaptureScreenshot = async () => {
          await recordImageStep('Manual Screenshot', {});
          if (isElectron() && window.api?.captureScreenshot) {
            return await window.api.captureScreenshot();
          } else {
            console.log('(Browser) Screenshot capture placeholder');
            return null;
          }
        };

        // ✅ FIX: Added missing comma before template literal
        const executeScript = new Function(
          'isElectron',
          'detectService',
          'findTextInImage',
          'performClick',
          'window',
          'captureScreenshot',
          'extractParagraphFromImage',
          `return (async () => { ${res.data.script} })();`
        );

        const detectServiceBound = async (testType, classID, image_data) => {
          await recordImageStep('Detection', { testType, classID, imageData: image_data ? 'provided' : 'captured' });
          return await detectService(testType, classID, image_data);
        };

        const findTextInImageBound = async (imageData, text) =>
          await wrappedFindTextInImage(imageData, text);

        await executeScript(
          isElectron,
          detectServiceBound,
          findTextInImageBound,
          wrappedPerformClick,
          window,
          wrappedCaptureScreenshot,
          extractParagraphFromImage
        );

        console.log('✅ Script execution finished');

        // Generate PDF report
        try {
          const payload = {
            test_id: res.data.test_id || null,
            gameUrl,
            testType,
            logs,
            steps,
          };
          const reportRes = await apiClient.post('/reports/generate', payload);
          console.log('📄 Report generated:', reportRes.data.url);
          res.data.report = reportRes.data;
          res.data.reportContext = payload;
        } catch (reportErr) {
          console.warn('Failed to generate report:', reportErr?.message || reportErr);
          res.data.reportContext = {
            test_id: res.data.test_id || null,
            gameUrl,
            testType,
            logs,
            steps,
          };
        }
      } finally {
        console.log = originalLog;
        console.warn = originalWarn;
        console.error = originalError;
      }
    } else {
      console.warn('⚠ No script found in backend response.');
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

/**
 * Report generation
 */
export const generateReport = async (reportContext) => {
  const res = await apiClient.post('/reports/generate', reportContext);
  return res.data;
};

/**
 * Detection service (per-step)
 */
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
 * OCR extract full paragraph
 */
const extractParagraphFromImage = async (imageData) => {
  try {
    const text="";
    const payload = { imageData  , text};
    const res = await apiClient.post('/ocr/extract-paragraph', payload);
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
 * OCR find specific text
 */
const findTextInImage = async (imageData, text) => {
  try {
    const payload = { imageData, text };
    const res = await apiClient.post('/ocr/find-text', payload);
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
