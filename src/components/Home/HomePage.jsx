import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  ShieldCheck,
  RotateCcw,
  Repeat,
  Banknote,
  PlayCircle,
  Maximize2,
  X,
} from 'lucide-react';
import { TEST_OPTIONS } from '../../constants/testOptions';
import { useStepwiseTest } from '../../hooks/useStepwiseTest';
import Toast from '../ui/Toast';
import LoadingSpinner from '../ui/LoadingSpinner';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import TestProgressPanel from '../components/TestProgressPanel'; // <-- EDIT: new progress panel

// Flow definitions for known test types (could eventually come from backend)
const FLOW_MAP = {
  Regression: [0, 1, 1, 15, 7, 10, 11],
};

const normalizeUrl = (raw) => {
  let url = raw.trim();
  if (!url) return '';
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }
  return url;
};

const HomePage = () => {
  const [gameUrl, setGameUrl] = useState('');
  const [testType, setTestType] = useState('Select a test type');
  const [urlError, setUrlError] = useState('');
  const [selectedSubTests, setSelectedSubTests] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const toastTimeoutRef = useRef(null);

  // ----------------- EDIT: using enhanced orchestrator with retry / override / cancel -----------------
  const {
    run,
    retryStep,
    overrideClickCoords,
    cancel,
    isRunning,
    currentClassId,
    history,
    finalResult,
    error: orchestratorError,
    reset: resetOrchestrator,
  } = useStepwiseTest();
  // ----------------------------------------------------------------------------------------------------

  // Local state to reflect flow for panel (fallback to static map)
  const [flow, setFlow] = useState([]);

  // Cleanup toast timer on unmount
  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

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

  const closeSubTestModal = () => setIsOpen(false);
  const openSubTestModal = () => setIsOpen(true);

  // Handle URL change
  const handleUrlChange = useCallback((e) => {
    const url = e.target.value;
    setGameUrl(url);
    setUrlError(''); // Clear any previous URL errors
  }, []);

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    toastTimeoutRef.current = window.setTimeout(() => {
      setToast(null);
      toastTimeoutRef.current = null;
    }, 5000); // Auto-dismiss after 5 seconds
  }, []);

  // Handler to open the game URL in controlled Electron window
  const handleOpenUrl = useCallback(() => {
    const urlToOpen = normalizeUrl(gameUrl);
    if (urlToOpen) {
      if (window.api && window.api.openTestWindow) {
        window.api.openTestWindow(urlToOpen);
        showToast('info', 'URL opened in controlled Electron window');
      } else {
        window.open(urlToOpen, '_blank', 'noopener,noreferrer');
        showToast('info', 'URL opened in new tab');
      }
    } else {
      showToast('error', 'Please enter a URL first');
    }
  }, [gameUrl, showToast]);

  // Handler to open the modal when a test type is selected
  const handleTestTypeChange = (e) => {
    const newTestType = e.target.value;
    setTestType(newTestType);
    setSelectedSubTests([]); // Reset sub-tests when the main test type changes
    openSubTestModal(); // Open the modal
  };

  // Toggle selection of a sub-test
  const handleSubTestToggle = useCallback(
    (sub) => {
      setSelectedSubTests((prev) =>
        prev.includes(sub) ? prev.filter((s) => s !== sub) : [...prev, sub]
      );
    },
    [setSelectedSubTests]
  );

  // ----------------- EDIT: orchestrator submit handler updated to capture flow & handle user controls -----------------
  const handleSubmit = async (e) => {
    e.preventDefault();

    resetOrchestrator();
    setFlow([]); // clear previous flow display

    if (!gameUrl.trim()) {
      setUrlError('URL is required.');
      showToast('error', 'Please enter a valid URL.');
      return;
    }

    const urlToOpen = normalizeUrl(gameUrl);
    if (!urlToOpen) {
      setUrlError('Invalid URL format.');
      showToast('error', 'Please enter a valid URL.');
      return;
    }

    try {
      // Open controlled window
      if (window.api && window.api.openTestWindow) {
        console.log(`Opening controlled test window for URL: ${urlToOpen}`);

        await window.api.openTestWindow(urlToOpen);
      } else {
        console.warn('Controlled test window API not available, opening in new tab');
        window.open(urlToOpen, '_blank', 'noopener,noreferrer');
      }

      // If we know a static flow for this type, set it (fallback)
      if (FLOW_MAP[testType]) {
        setFlow(FLOW_MAP[testType]);
      } else {
        setFlow([]); // unknown until backend could supply if extended
      }

      // Kick off the orchestration
      await run(
        { gameUrl, testType },
        ({ step_result, next_step, status }) => {
          if (step_result.passed) {
            showToast(
              'success',
              `Class ID ${step_result.class_id} passed (confidence: ${step_result.detection?.confidence?.toFixed(2) || 'N/A'
              })`
            );
          } else {
            showToast('error', `Class ID ${step_result.class_id} failed, retrying if allowed`);
          }
          // If backend ever included dynamic flow in next_step, could update flow here
        }
      );
      showToast('success', 'Test flow complete');
    } catch (err) {
      showToast('error', err.message || 'Test failed');
    }
  };
  // --------------------------------------------------------------------------------------------------------------

  // Sub-panel control callbacks
  const handleRetry = async (classId) => {
    try {
      await retryStep(classId, ({ step_result, next_step, status }) => {
        showToast(
          step_result.passed ? 'success' : 'error',
          `Retry class ${classId} ${step_result.passed ? 'passed' : 'failed'}`
        );
      });
    } catch (err) {
      showToast('error', `Retry failed: ${err.message}`);
    }
  };

  const handleOverrideClick = (classId, x, y) => {
    overrideClickCoords(classId, x, y);
    showToast('info', `Override click for class ${classId} set to (${x.toFixed(1)}, ${y.toFixed(1)})`);
  };

  const handleAbort = () => {
    cancel();
    showToast('info', 'Test aborted by user');
  };

  // Get all sub-test types for the current test type
  const allSubTestOptions =
    TEST_OPTIONS.find((opt) => opt.label === testType)?.test_types || [];

  return (
    <div className="fixed inset-0 overflow-auto w-screen min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start px-4 py-6">
      {/* Hero Section */}
      <section className="text-center mb-6 w-full max-w-2xl">
        <h1 className="text-4xl md:text-5xl font-bold text-green-400 mb-2">
          Automated Compliance Test.
        </h1>
        <p className="text-lg md:text-xl text-gray-300">
          A smart platform for automated regulatory compliance testing.
        </p>
      </section>

      {/* Form + Control Section */}
      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: form */}
        <div className="bg-gray-800 rounded-2xl shadow-lg p-6">
          <form onSubmit={handleSubmit}>
            {/* Game URL */}
            <div className="mb-4">
              <label htmlFor="gameUrl" className="block mb-1 text-sm font-medium text-blue-300">
                Game URL *
              </label>
              <input
                id="gameUrl"
                type="url"
                placeholder="Enter game URL (e.g., https://example.com)"
                className={`w-full px-4 py-2 rounded-lg bg-gray-700 text-white border ${urlError ? 'border-red-500' : 'border-gray-600'
                  } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                value={gameUrl}
                onChange={handleUrlChange}
                required
                disabled={isRunning}
              />
              {urlError && <p className="mt-1 text-sm text-red-400">{urlError}</p>}
            </div>

            {/* Test Type Dropdown */}
            <div className="mb-4">
              <label htmlFor="testType" className="block mb-1 text-sm font-medium text-blue-300">
                Select Test Type *
              </label>
              <select
                id="testType"
                className="w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                value={testType}
                onChange={handleTestTypeChange}
                disabled={isRunning}
              >
                <option value="Select a test type" disabled>
                  -- Select a test type --
                </option>
                {TEST_OPTIONS.map((opt, idx) => (
                  <option key={idx} value={opt.label} title={opt.description}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Selected Sub-tests Display */}
            {selectedSubTests.length > 0 && (
              <div className="mb-4">
                <h3 className="block mb-1 text-sm font-medium text-blue-300">
                  Selected Sub-tests:
                </h3>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedSubTests.map((sub, idx) => (
                    <span
                      key={idx}
                      className="flex items-center bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium shadow border border-blue-400"
                    >
                      {getIcon('ShieldCheck', 'mr-1')}
                      {sub}
                      <button
                        type="button"
                        className="ml-2 text-white hover:text-red-300 focus:outline-none"
                        onClick={() => handleSubTestToggle(sub)}
                        aria-label={`Remove ${sub}`}
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Orchestrator Error */}
            {orchestratorError && (
              <div className="mb-4 p-3 bg-red-900 border border-red-600 rounded-lg">
                <p className="text-sm text-red-200">
                  {orchestratorError.message || String(orchestratorError)}
                </p>
              </div>
            )}


            {/* Final Result Summary (compact) */}
            {finalResult && (
              <div className="mb-4 p-3 bg-green-900 border border-green-600 rounded-lg">
                <p className="text-sm text-green-200">
                  Final Status: {finalResult.status || 'success'}
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="text-center mt-4 space-y-3">
              <button
                type="button"
                onClick={handleOpenUrl}
                className="w-full bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:cursor-not-allowed text-white px-5 py-2 rounded-xl font-semibold shadow-md transition-all duration-300"
                disabled={!gameUrl.trim() || isRunning}
              >
                🔗 Open URL in Controlled Window
              </button>
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600 disabled:cursor-not-allowed text-white px-5 py-2 rounded-xl font-semibold shadow-md transition-all duration-300"
                disabled={isRunning}
              >
                {isRunning ? <LoadingSpinner text="Running Stepwise Test..." /> : '🚀 Run Compliance Test'}
              </button>
              {isRunning && (
                <button
                  type="button"
                  onClick={handleAbort}
                  className="w-full bg-red-600 hover:bg-red-700 text-white px-5 py-2 rounded-xl font-semibold shadow-md transition-all duration-300"
                >
                  ✋ Abort Test
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Right: progress panel */}
        <div className="space-y-4">
          <TestProgressPanel
            flow={flow}
            history={history}
            currentClassId={currentClassId}
            finalResult={finalResult}
            onRetryStep={handleRetry}
            onAbort={handleAbort}
            onOverrideClick={handleOverrideClick}
          />
        </div>
      </div>

      {/* Sub-test Selection Modal */}
      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={closeSubTestModal}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-75" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-xl transform overflow-hidden rounded-2xl bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-bold leading-6 text-green-400 flex justify-between items-center"
                  >
                    Select Sub-tests for "{testType}"
                    <button
                      type="button"
                      onClick={closeSubTestModal}
                      className="p-1 rounded-full text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </Dialog.Title>
                  <div className="mt-4">
                    <p className="text-sm text-gray-400 mb-4">
                      Choose which specific tests you want to run within the "{testType}" category.
                    </p>
                    <div className="max-h-80 overflow-y-auto pr-2 grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {allSubTestOptions.length > 0 ? (
                        allSubTestOptions.map((sub, idx) => {
                          const isSelected = selectedSubTests.includes(sub);
                          return (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => handleSubTestToggle(sub)}
                              className={`w-full text-left p-4 rounded-xl shadow-lg transition-all duration-200 border-2 flex items-center gap-2
                                ${isSelected
                                  ? 'bg-blue-600 border-blue-400 ring-2 ring-blue-500'
                                  : 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                              disabled={isRunning}
                            >
                              {getIcon(
                                'ShieldCheck',
                                isSelected ? 'text-white' : 'text-green-400'
                              )}
                              <span className="break-words whitespace-normal text-sm font-semibold text-white">
                                {sub}
                              </span>
                            </button>
                          );
                        })
                      ) : (
                        <p className="text-gray-400 text-center py-4 col-span-2">
                          No sub-test types available for this selection.
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="mt-6 flex justify-end gap-3">
                    <button
                      type="button"
                      className="inline-flex justify-center rounded-md border border-transparent bg-gray-600 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-500 focus-visible:ring-offset-2"
                      onClick={closeSubTestModal}
                    >
                      Done
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>

      {/* Toast Notifications */}
      {toast && (
        <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />
      )}
    </div>
  );
};

export default HomePage;
