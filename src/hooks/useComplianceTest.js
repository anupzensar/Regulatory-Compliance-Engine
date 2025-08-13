import { useState, useCallback } from 'react';
import { submitComplianceTest } from '../services/api';

export const useComplianceTest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const runTest = useCallback(async (gameUrl, selectedPolicy, selectedTestSuite, selectedTestCases) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      let testType = selectedTestSuite || 'Session Reminder';
      response = await submitComplianceTest(gameUrl,testType, selectedPolicy, selectedTestSuite, selectedTestCases);

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
