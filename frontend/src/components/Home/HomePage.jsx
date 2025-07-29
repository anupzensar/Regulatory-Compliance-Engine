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

const HomePage = () => {
  const [gameUrl, setGameUrl] = useState("");
  const [testType, setTestType] = useState(TEST_OPTIONS[0].label);
  const [urlError, setUrlError] = useState("");
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
      
      const response = await runTest(gameUrl, testType);
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
        <h1 className="text-3xl md:text-4xl font-bold text-green-400 mb-2">
          Automated Compliance Test.
        </h1>
        <p className="text-gray-300 text-base md:text-lg">
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
            onChange={e => setTestType(e.target.value)}
            disabled={isLoading}
          >
            {TEST_OPTIONS.map((opt, idx) => (
              <option key={idx} value={opt.label} title={opt.description}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

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

export default HomePage;
