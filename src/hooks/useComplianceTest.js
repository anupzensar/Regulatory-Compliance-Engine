import { useState, useCallback } from 'react';
import { submitComplianceTest } from '../services/api';

/**
 * NOTE: For stepwise flows like Regression (with /run-test-step and
 * per-class orchestration), prefer using `useStepwiseTest` instead.
 * This hook remains as a simpler fallback for non-stepwise or legacy flows.
 */
export const useComplianceTest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  /**
   * Runs a compliance test. 
   * @param {string} gameUrl
   * @param {string} testType
   * @param {Array} selectedSubTests - optional; currently passed through if provided
   */
  const runTest = useCallback(async (gameUrl, testType, selectedSubTests = []) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build payload. Back-end currently accepts gameUrl and testType;
      // include sub-tests if present (backend may ignore if not expected).
      let response;
      if (selectedSubTests && selectedSubTests.length > 0) {
        // If backend is updated to support sub-tests, it should read this field.
        response = await submitComplianceTest(gameUrl, testType, selectedSubTests);
      } else {
        response = await submitComplianceTest(gameUrl, testType);
      }

      setResult(response);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
  }, []);

  return {
    isLoading,
    error,
    result,
    runTest,
    clearError,
    clearResult,
  };
};
