import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Moon,
  Sun,
  Settings,
  Link,
  ChevronDown,
  CheckSquare,
  Square,
} from 'lucide-react';
import { GOVERNMENT_POLICIES, TEST_SUITES } from '../../constants/testOptions';
import { useStepwiseTest } from '../../hooks/useStepwiseTest';
import Toast from '../ui/Toast';
import LoadingSpinner from '../ui/LoadingSpinner';

const normalizeUrl = (raw) => {
  let url = raw.trim();
  if (!url) return '';
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }
  return url;
};

const HomePage = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [gameUrl, setGameUrl] = useState('');
  const [selectedPolicy, setSelectedPolicy] = useState('');
  const [selectedTestSuite, setSelectedTestSuite] = useState('');
  const [selectedTestCases, setSelectedTestCases] = useState([]);
  const [toast, setToast] = useState(null);
  const toastTimeoutRef = useRef(null);

  const {
    run,
    isRunning,
    currentClassId,
    history,
    finalResult,
    error: orchestratorError,
    reset: resetOrchestrator,
  } = useStepwiseTest();

  // Cleanup toast timer on unmount
  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    toastTimeoutRef.current = window.setTimeout(() => {
      setToast(null);
      toastTimeoutRef.current = null;
    }, 5000);
  }, []);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleUrlChange = useCallback((e) => {
    setGameUrl(e.target.value);
  }, []);

  const handlePolicyChange = (e) => {
    setSelectedPolicy(e.target.value);
  };

  const handleTestSuiteChange = (e) => {
    setSelectedTestSuite(e.target.value);
    setSelectedTestCases([]); // Reset selected test cases when suite changes
  };

  const handleTestCaseToggle = (testCaseId) => {
    setSelectedTestCases(prev => 
      prev.includes(testCaseId) 
        ? prev.filter(id => id !== testCaseId)
        : [...prev, testCaseId]
    );
  };

  const handleSelectAll = () => {
    const currentSuite = TEST_SUITES.find(suite => suite.value === selectedTestSuite);
    if (currentSuite) {
      const allTestCaseIds = currentSuite.test_cases.map(tc => tc.id);
      setSelectedTestCases(allTestCaseIds);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    resetOrchestrator();

    if (!gameUrl.trim()) {
      showToast('error', 'Please enter a valid URL.');
      return;
    }

    if (!selectedPolicy) {
      showToast('error', 'Please select a government policy.');
      return;
    }

    if (!selectedTestSuite) {
      showToast('error', 'Please select a test suite.');
      return;
    }

    if (selectedTestCases.length === 0) {
      showToast('error', 'Please select at least one test case.');
      return;
    }

    const urlToOpen = normalizeUrl(gameUrl);

    try {
      // Open controlled window
      if (window.api && window.api.openTestWindow) {
        console.log(`Opening controlled test window for URL: ${urlToOpen}`);
        await window.api.openTestWindow(urlToOpen);
      } else {
        console.warn('Controlled test window API not available, opening in new tab');
        window.open(urlToOpen, '_blank', 'noopener,noreferrer');
      }

      // Run the test
      await run(
        { gameUrl, testType: selectedTestSuite },
        ({ step_result, next_step, status }) => {
          if (step_result.passed) {
            showToast(
              'success',
              `Class ID ${step_result.class_id} passed (confidence: ${step_result.detection?.confidence?.toFixed(2) || 'N/A'})`
            );
          } else {
            showToast('error', `Class ID ${step_result.class_id} failed, retrying if allowed`);
          }
        }
      );
      showToast('success', 'Test flow complete');
    } catch (err) {
      showToast('error', err.message || 'Test failed');
    }
  };

  const currentTestSuite = TEST_SUITES.find(suite => suite.value === selectedTestSuite);
  const availableTestCases = currentTestSuite ? currentTestSuite.test_cases : [];

  const themeClasses = isDarkMode 
    ? 'bg-slate-800 text-white' 
    : 'bg-gray-50 text-gray-900';

  const cardClasses = isDarkMode 
    ? 'bg-slate-700 border-slate-600' 
    : 'bg-white border-gray-200';

  const inputClasses = isDarkMode 
    ? 'bg-slate-600 border-slate-500 text-white placeholder-slate-400' 
    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500';

  const selectClasses = isDarkMode 
    ? 'bg-slate-600 border-slate-500 text-white' 
    : 'bg-white border-gray-300 text-gray-900';

  const testCaseClasses = isDarkMode 
    ? 'bg-slate-600 border-slate-500' 
    : 'bg-gray-100 border-gray-300';

  return (
    <div className={`min-h-screen ${themeClasses} transition-colors duration-200`}>
      {/* Header */}
      <header className={`${isDarkMode ? 'bg-slate-700' : 'bg-white'} border-b ${isDarkMode ? 'border-slate-600' : 'border-gray-200'} px-6 py-4`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 ${isDarkMode ? 'bg-slate-600' : 'bg-gray-200'} rounded-lg flex items-center justify-center`}>
              <span className="text-lg font-bold">RCE</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg ${isDarkMode ? 'bg-slate-600 hover:bg-slate-500' : 'bg-gray-200 hover:bg-gray-300'} transition-colors`}
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button className={`p-2 rounded-lg ${isDarkMode ? 'bg-slate-600 hover:bg-slate-500' : 'bg-gray-200 hover:bg-gray-300'} transition-colors`}>
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* URL Input */}
          <div className={`${cardClasses} rounded-lg border p-6`}>
            <div className="flex items-center space-x-3 mb-4">
              <Link className={`w-5 h-5 ${isDarkMode ? 'text-slate-400' : 'text-gray-500'}`} />
              <input
                type="url"
                placeholder="Paste Here..."
                value={gameUrl}
                onChange={handleUrlChange}
                className={`flex-1 px-4 py-3 rounded-lg border ${inputClasses} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                required
                disabled={isRunning}
              />
            </div>
          </div>

          {/* Dropdowns */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Government Policy Dropdown */}
            <div className="relative">
              <select
                value={selectedPolicy}
                onChange={handlePolicyChange}
                className={`w-full px-4 py-3 rounded-lg border ${selectClasses} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none`}
                required
                disabled={isRunning}
              >
                <option value="">Choose Gov Policy</option>
                {GOVERNMENT_POLICIES.map((policy) => (
                  <option key={policy.value} value={policy.value}>
                    {policy.label}
                  </option>
                ))}
              </select>
              <ChevronDown className={`absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${isDarkMode ? 'text-slate-400' : 'text-gray-500'} pointer-events-none`} />
            </div>

            {/* Test Suite Dropdown */}
            <div className="relative">
              <select
                value={selectedTestSuite}
                onChange={handleTestSuiteChange}
                className={`w-full px-4 py-3 rounded-lg border ${selectClasses} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none`}
                required
                disabled={isRunning}
              >
                <option value="">Choose Test Case</option>
                {TEST_SUITES.map((suite) => (
                  <option key={suite.value} value={suite.value}>
                    {suite.label}
                  </option>
                ))}
              </select>
              <ChevronDown className={`absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${isDarkMode ? 'text-slate-400' : 'text-gray-500'} pointer-events-none`} />
            </div>
          </div>

          {/* Test Cases Selection */}
          {availableTestCases.length > 0 && (
            <div className={`${cardClasses} rounded-lg border p-6`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Select cases</h3>
                <button
                  type="button"
                  onClick={handleSelectAll}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  disabled={isRunning}
                >
                  Select all
                </button>
              </div>

              <div className="space-y-3">
                {availableTestCases.map((testCase) => {
                  const isSelected = selectedTestCases.includes(testCase.id);
                  return (
                    <div
                      key={testCase.id}
                      className={`flex items-center justify-between p-4 rounded-lg border ${testCaseClasses} hover:${isDarkMode ? 'bg-slate-500' : 'bg-gray-50'} transition-colors cursor-pointer`}
                      onClick={() => handleTestCaseToggle(testCase.id)}
                    >
                      <div className="flex items-center space-x-3">
                        {isSelected ? (
                          <CheckSquare className="w-5 h-5 text-blue-600" />
                        ) : (
                          <Square className={`w-5 h-5 ${isDarkMode ? 'text-slate-400' : 'text-gray-400'}`} />
                        )}
                        <div>
                          <h4 className="font-medium">{testCase.name}</h4>
                          <p className={`text-sm ${isDarkMode ? 'text-slate-400' : 'text-gray-500'}`}>
                            {testCase.description}
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        className={`px-3 py-1 rounded-md text-sm ${isDarkMode ? 'bg-slate-500 hover:bg-slate-400 text-slate-200' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'} transition-colors`}
                      >
                        Details
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Error Display */}
          {orchestratorError && (
            <div className="p-4 bg-red-900 border border-red-600 rounded-lg">
              <p className="text-sm text-red-200">
                {orchestratorError.message || String(orchestratorError)}
              </p>
            </div>
          )}

          {/* Final Result */}
          {finalResult && (
            <div className="p-4 bg-green-900 border border-green-600 rounded-lg">
              <p className="text-sm text-green-200">
                Final Status: {finalResult.status || 'success'}
              </p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-600 disabled:cursor-not-allowed font-semibold transition-colors min-w-48"
              disabled={isRunning}
            >
              {isRunning ? <LoadingSpinner text="Running Tests..." /> : 'Run Selected Tests'}
            </button>
          </div>
        </form>
      </main>

      {/* Toast Notifications */}
      {toast && (
        <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />
      )}
    </div>
  );
};

export default HomePage;