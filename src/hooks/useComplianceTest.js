import { useState, useCallback } from 'react';
import { submitComplianceTest, launchRegression } from '../services/api';

export const useComplianceTest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const runTest = useCallback(async (gameUrl, testType, selectedSubTests) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      if (testType === 'Regression Testing') {
        response = await launchRegression(gameUrl, true); // headless true by default
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
