import React, { useState, useCallback } from 'react';
import {
  ShieldCheck,
  RotateCcw,
  Repeat,
  Banknote,
  PlayCircle,
  Maximize2,
} from 'lucide-react';
import { TEST_OPTIONS } from '../../constants/testOptions';
import { useComplianceTest } from '../../hooks/useComplianceTest';
import Toast from '../ui/Toast';
import LoadingSpinner from '../ui/LoadingSpinner';
import { Listbox } from '@headlessui/react';
import { ChevronUpDownIcon } from '@heroicons/react/20/solid';

const HomePage2 = () => {
  const [gameUrl, setGameUrl] = useState("");
  const [testType, setTestType] = useState(TEST_OPTIONS[0].label);
  const [urlError, setUrlError] = useState("");
  const [selectedSubTests, setSelectedSubTests] = useState([]);
  const [subTestToAdd, setSubTestToAdd] = useState("");

  const [toast, setToast] = useState(null);

  const { isLoading, error, result, runTest, clearError } = useComplianceTest();

  // Helper function to render icons
  const getIcon = (iconName, iconColor) => {
    const iconProps = { className: `w-5 h-5 ${iconColor}` };
    switch (iconName) {
      case 'ShieldCheck':
        return <ShieldCheck {...iconProps} />;
      case 'RotateCcw':
        return <RotateCcw {...iconProps} />;
      case 'Repeat':
        return <Repeat {...iconProps} />;
      case 'Banknote':
        return <Banknote {...iconProps} />;
      case 'PlayCircle':
        return <PlayCircle {...iconProps} />;
      case 'Maximize2':
        return <Maximize2 {...iconProps} />;
      default:
        return null;
    }
  };

  // Handle URL change
  const handleUrlChange = useCallback((e) => {
    const url = e.target.value;
    setGameUrl(url);
    setUrlError(""); // Clear any previous URL errors
  }, []);

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000); // Auto-dismiss after 5 seconds
  }, []);

  const handleOpenUrl = useCallback(() => {
    if (gameUrl.trim()) {
      // Ensure URL has protocol if missing
      let urlToOpen = gameUrl.trim();
      if (!urlToOpen.startsWith('http://') && !urlToOpen.startsWith('https://')) {
        urlToOpen = 'https://' + urlToOpen;
      }

      // Open URL in new tab
      window.open(urlToOpen, '_blank', 'noopener,noreferrer');
      showToast('info', 'URL opened in new tab');
    } else {
      showToast('error', 'Please enter a URL first');
    }
  }, [gameUrl, showToast]);

  // Get sub test types for the selected test type, excluding already selected
  const subTestOptions = (TEST_OPTIONS.find(opt => opt.label === testType)?.test_types || []).filter(sub => !selectedSubTests.includes(sub));

  // Handle sub test type selection (single select for add)
  const handleSubTestSelect = useCallback((e) => {
    setSubTestToAdd(e.target.value);
  }, []);

  // Add selected sub test type to the list
  const handleAddSubTest = useCallback(() => {
    if (subTestToAdd && !selectedSubTests.includes(subTestToAdd)) {
      setSelectedSubTests(prev => [...prev, subTestToAdd]);
      setSubTestToAdd("");
    }
  }, [subTestToAdd, selectedSubTests]);

  // Remove a sub test type
  const handleRemoveSubTest = useCallback((sub) => {
    setSelectedSubTests(prev => prev.filter(s => s !== sub));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Clear any previous errors
    clearError();

    try {
      // Launch the URL in a new tab before submitting the test
      if (gameUrl.trim()) {
        // Ensure URL has protocol if missing
        let urlToOpen = gameUrl.trim();
        if (!urlToOpen.startsWith('http://') && !urlToOpen.startsWith('https://')) {
          urlToOpen = 'https://' + urlToOpen;
        }

        // Open URL in new tab
        window.open(urlToOpen, '_blank', 'noopener,noreferrer');
      }

      // Pass selectedSubTests to runTest
      const response = await runTest(gameUrl, testType, selectedSubTests);
      showToast('success', `Test submitted successfully! Test ID: ${response.test_id}`);

      // Optional: Reset form after successful submission
      // setGameUrl("");
      // setTestType(TEST_OPTIONS[0].label);

    } catch (err) {
      showToast('error', err.message || 'Failed to submit test');
    }
  };

  return (
    <div className="fixed inset-0 overflow-hidden w-screen h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-4">
      {/* Hero Section */}
      <section className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-bold text-green-400 mb-2"> {/* Increased text size here */}
          Automated Compliance Test.
        </h1>
        <p className="text-lg md:text-xl text-gray-300"> {/* Increased text size here */}
          A smart platform for automated regulatory compliance testing.
        </p>
      </section>

      {/* Form Section */}
      <form onSubmit={handleSubmit} className="w-full max-w-lg bg-gray-800 rounded-2xl shadow-lg p-6">
        {/* Game URL */}
        <div className="mb-4">
          <label htmlFor="gameUrl" className="block mb-1 text-sm font-medium text-blue-300">
            Game URL *
          </label>
          <input
            id="gameUrl"
            type="url"
            placeholder="Enter game URL (e.g., https://example.com)"
            className={`w-full px-4 py-2 rounded-lg bg-gray-700 text-white border ${urlError ? 'border-red-500' : 'border-gray-600'} focus:outline-none focus:ring-2 focus:ring-blue-500`}
            value={gameUrl}
            onChange={handleUrlChange}
            required
            disabled={isLoading}
          />
          {urlError && (
            <p className="mt-1 text-sm text-red-400">{urlError}</p>
          )}
        </div>

        {/* Dropdown */}
        <div className="mb-4">
          <label htmlFor="testType" className="block mb-1 text-sm font-medium text-blue-300">
            Select Test Type *
          </label>
          <select
            id="testType"
            className="w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
            value={testType}
            onChange={e => { setTestType(e.target.value); setSelectedSubTests([]); }}
            disabled={isLoading}
          >
            {TEST_OPTIONS.map((opt, idx) => (
              <option key={idx} value={opt.label} title={opt.description}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sub Test Types Select & Chips (using a custom scrollable list) */}
        {((TEST_OPTIONS.find(opt => opt.label === testType)?.test_types || []).length > 0) && (
          <div className="mb-4">
            <label htmlFor="subTestTypes" className="block mb-1 text-sm font-medium text-blue-300">
              Select Sub Test Types
            </label>
            {/* Card grid of sub-test options (no scroll) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 rounded-lg border border-gray-600 bg-gray-700 p-2">
              {(TEST_OPTIONS.find(opt => opt.label === testType)?.test_types || []).map((sub, idx) => {
                const isSelected = selectedSubTests.includes(sub);
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      if (isSelected) {
                        setSelectedSubTests(prev => prev.filter(s => s !== sub));
                      } else {
                        setSelectedSubTests(prev => [...prev, sub]);
                      }
                    }}
                    disabled={isLoading}
                    className={`w-full text-left p-4 rounded-xl shadow transition-all duration-200 border-2 flex items-center gap-2 bg-gray-800 hover:bg-gray-700 focus:outline-none
                      ${isSelected ? 'border-green-500 ring-2 ring-green-400' : 'border-gray-600'}
                      ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    title={sub}
                  >
                    {getIcon('ShieldCheck', isSelected ? 'text-green-400' : 'text-white')}
                    <span className="break-words whitespace-normal text-sm font-semibold">{sub}</span>
                  </button>
                );
              })}
            </div>
            {/* Selected items as chips */}
            <div className="flex flex-wrap gap-2 mt-3">
              {selectedSubTests.map((sub, idx) => (
                <span
                  key={idx}
                  className="flex items-center bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium shadow border border-blue-400 whitespace-normal"
                >
                  {getIcon('ShieldCheck', 'mr-1')}
                  {sub}
                  <button
                    type="button"
                    className="ml-2 text-white hover:text-red-300 focus:outline-none"
                    onClick={() => handleRemoveSubTest(sub)}
                    aria-label={`Remove ${sub}`}
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-900 border border-red-600 rounded-lg">
            <p className="text-sm text-red-200">{error}</p>
          </div>
        )}

        {/* Success Display */}
        {result && (
          <div className="mb-4 p-3 bg-green-900 border border-green-600 rounded-lg">
            <p className="text-sm text-green-200">{result.message}</p>
            {result.test_id && (
              <p className="text-xs text-green-300 mt-1">Test ID: {result.test_id}</p>
            )}
          </div>
        )}

        {/* Submit Button */}
        <div className="text-center mt-4 space-y-3">
          {/* Open URL Button */}
          <button
            type="button"
            onClick={handleOpenUrl}
            className="w-full bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:cursor-not-allowed text-white px-5 py-2 rounded-xl font-semibold shadow-md transition-all duration-300"
            disabled={!gameUrl.trim() || isLoading}
          >
            🔗 Open URL in New Tab
          </button>


          {/* Submit Test Button */}
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-5 py-2 rounded-xl font-semibold shadow-md transition-all duration-300"
            disabled={isLoading}
          >
            {isLoading ? (
              <LoadingSpinner text="Running Test..." />
            ) : (
              "🚀 Run Compliance Test & Open URL"
            )}
          </button>
        </div>
      </form>

      {/* Toast Notifications */}
      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

export default HomePage2;
