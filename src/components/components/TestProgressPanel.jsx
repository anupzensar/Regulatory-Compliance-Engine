import React from 'react';
import { X, RefreshCcw, CheckCircle, AlertCircle, Circle } from 'lucide-react';

const statusBadge = (step, isCurrent) => {
    if (step.passed) {
        return (
            <div className="flex items-center text-green-300 space-x-1">
                <CheckCircle className="w-4 h-4" />
                <span className="text-xs font-semibold">Passed</span>
            </div>
        );
    }
    if (!step.passed && isCurrent) {
        return (
            <div className="flex items-center text-yellow-300 space-x-1">
                <RefreshCcw className="w-4 h-4 animate-spin" />
                <span className="text-xs font-semibold">In progress</span>
            </div>
        );
    }
    if (!step.passed) {
        return (
            <div className="flex items-center text-red-300 space-x-1">
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-semibold">Failed</span>
            </div>
        );
    }
    return (
        <div className="flex items-center text-gray-400 space-x-1">
            <Circle className="w-4 h-4" />
            <span className="text-xs font-semibold">Pending</span>
        </div>
    );
};

const TestProgressPanel = ({
    flow = [],
    history = [],
    currentClassId,
    finalResult,
    onRetryStep,
    onAbort,
    onOverrideClick,
}) => {
    // For each step in flow, find the nth occurrence in history
    const stepHistory = flow.map((classId, idx) => {
        let occurrence = 0;
        for (let i = 0; i < idx; i++) {
            if (flow[i] === classId) occurrence++;
        }
        let found = null;
        let count = 0;
        for (const step of history) {
            if (step.class_id === classId) {
                if (count === occurrence) {
                    found = step;
                    break;
                }
                count++;
            }
        }
        return found;
    });

    // Find the current step index in flow (by occurrence)
    const currentStepIdx = (() => {
        let idx = -1;
        let occurrence = 0;
        for (let i = 0; i < flow.length; i++) {
            if (flow[i] === currentClassId) {
                // Count how many times currentClassId has appeared so far in history
                let count = 0;
                for (const step of history) {
                    if (step.class_id === currentClassId) count++;
                }
                if (occurrence === count - 1) {
                    idx = i;
                    break;
                }
                occurrence++;
            }
        }
        return idx;
    })();

    return (
        <div className="bg-gray-800 rounded-2xl shadow-lg p-4 space-y-4">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-lg font-bold text-white">Test Progress</h2>
                    <p className="text-sm text-gray-400">Flow: {flow.join(' → ')}</p>
                </div>
                <div className="flex gap-2">
                    {onAbort && (
                        <button
                            onClick={onAbort}
                            className="flex items-center gap-1 bg-red-600 hover:bg-red-700 px-3 py-1 rounded-md text-xs font-semibold"
                        >
                            <X className="w-4 h-4" /> Abort
                        </button>
                    )}
                </div>
            </div>

            {/* Step sequence overview with vertical scroll and hidden scrollbar */}
            <div
                className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-96 overflow-y-auto"
                style={{
                    scrollbarWidth: 'none', // Firefox
                    msOverflowStyle: 'none', // IE 10+
                }}
            >
                {flow.map((classId, idx) => {
                    const step = stepHistory[idx];
                    const isCurrent = idx === currentStepIdx && !(finalResult && finalResult.status);
                    return (
                        <div
                            key={idx}
                            className={`flex flex-col p-3 rounded-xl border ${step
                                ? step.passed
                                    ? 'border-green-500 bg-green-900/20'
                                    : 'border-red-500 bg-red-900/20'
                                : isCurrent
                                    ? 'border-yellow-400 bg-yellow-900/10'
                                    : 'border-gray-600 bg-gray-900/10'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-1">
                                <div className="flex items-center gap-2">
                                    <div className="text-xs font-bold text-white">
                                        Class ID: {classId} <span className="text-gray-400">#{idx + 1}</span>
                                    </div>
                                    {isCurrent && (
                                        <div className="text-xs px-2 py-0.5 bg-yellow-700 rounded-full text-yellow-100">
                                            Active
                                        </div>
                                    )}
                                </div>
                                <div>{step ? statusBadge(step, isCurrent) : <div className="text-xs text-gray-400">Not started</div>}</div>
                            </div>

                            {/* Details if step exists */}
                            {step && (
                                <div className="text-xs text-gray-300 space-y-1">
                                    <div>
                                        <strong>Passed:</strong> {step.passed ? 'Yes' : 'No'}
                                    </div>
                                    <div>
                                        <strong>Confidence:</strong>{' '}
                                        {step.detection?.confidence != null
                                            ? step.detection.confidence.toFixed(2)
                                            : 'N/A'}
                                    </div>
                                    {step.detection && step.detection.click_x != null && (
                                        <div>
                                            <strong>Click coords:</strong>{' '}
                                            ({step.detection.click_x.toFixed(1)},{' '}
                                            {step.detection.click_y.toFixed(1)})
                                        </div>
                                    )}
                                    {step.detection?.bounding_box && (
                                        <div>
                                            <strong>BBox:</strong>{' '}
                                            {`[${step.detection.bounding_box.x1}, ${step.detection.bounding_box.y1}] → [${step.detection.bounding_box.x2}, ${step.detection.bounding_box.y2}]`}
                                        </div>
                                    )}
                                    {/* Retry / override actions */}
                                    <div className="flex gap-2 mt-2">
                                        {/*
                                        // Retry button: Allows user to retry detection for this classId if step failed
                                        // Calls onRetryStep(classId) when clicked
                                        {!step.passed && onRetryStep && (
                                            <button
                                                onClick={() => onRetryStep(classId)}
                                                className="flex items-center gap-1 bg-yellow-500 hover:bg-yellow-600 px-2 py-1 rounded-md text-[10px] font-semibold"
                                            >
                                                <RefreshCcw className="w-3 h-3" /> Retry
                                            </button>
                                        )}
                                        */}
                                        {/*
                                        // Override Click button: Allows user to manually trigger a click at detected coordinates
                                        // Calls onOverrideClick(classId, x, y) when clicked, using detection's click_x and click_y (or 0 if not available)
                                        {onOverrideClick && (
                                            <button
                                                onClick={() => {
                                                    const x = step.detection?.click_x || 0;
                                                    const y = step.detection?.click_y || 0;
                                                    onOverrideClick(classId, x, y);
                                                }}
                                                className="flex items-center gap-1 bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded-md text-[10px] font-semibold"
                                            >
                                                Override Click
                                            </button>
                                        )}
                                        */}
                                    </div>
                                </div>
                            )}

                            {/* Placeholder if not yet executed */}
                            {!step && isCurrent && (
                                <div className="text-xs text-gray-300 mt-1">
                                    Waiting for execution of class_id {classId}...
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Hide scrollbar visually */}
            <style>{`
                .grid-cols-1::-webkit-scrollbar, .grid-cols-2::-webkit-scrollbar {
                    display: none;
                }
            `}</style>

            {/* Final result summary */}
            {finalResult && (
                <div className="mt-2 p-3 bg-gray-900 border border-green-500 rounded-lg">
                    <div className="flex justify-between items-center">
                        <div className="text-sm font-medium text-white">
                            Final Result:{' '}
                            <span className="font-bold">
                                {finalResult.status || (finalResult.success ? 'success' : 'unknown')}
                            </span>
                        </div>
                        {finalResult.status === 'success' && (
                            <div className="text-green-400 flex items-center gap-1">
                                <CheckCircle className="w-5 h-5" /> Success
                            </div>
                        )}
                        {finalResult.status !== 'success' && (
                            <div className="text-red-400 flex items-center gap-1">
                                <AlertCircle className="w-5 h-5" /> {finalResult.status || 'Failed'}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TestProgressPanel;
