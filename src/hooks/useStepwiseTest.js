import { useState, useCallback, useRef } from 'react';
import {
    startRegressionTest,
    submitTestStep,
    submitComplianceTest,
} from '../services/api';

/**
 * Hook to orchestrate a stepwise test flow (e.g., Regression with class flow).
 * Enhancements added:
 *  - retryStep: allow external retry of a specific failed class_id
 *  - overrideClickCoords: inject manual click coordinates instead of using detection
 *  - clear separation of automatic loop vs. user-triggered interventions
 */
export const useStepwiseTest = () => {
    const [isRunning, setIsRunning] = useState(false);
    const [currentClassId, setCurrentClassId] = useState(null);
    const [history, setHistory] = useState([]); // array of step_result objects
    const [finalResult, setFinalResult] = useState(null);
    const [error, setError] = useState(null);

    // Internal mutable refs
    const cancelRef = useRef(false);
    const testIdRef = useRef(null);
    const lastStepResponsesRef = useRef({}); // map class_id -> last step_resp
    const overrideClicksRef = useRef({}); // map class_id -> { x, y }

    // Add a step result to history (dedupe by appending; history order matters)
    const pushHistory = useCallback((stepResult) => {
        setHistory((h) => [...h, stepResult]);
    }, []);

    const reset = useCallback(() => {
        cancelRef.current = false;
        setIsRunning(false);
        setCurrentClassId(null);
        setHistory([]);
        setFinalResult(null);
        setError(null);
        testIdRef.current = null;
        lastStepResponsesRef.current = {};
        overrideClicksRef.current = {};
    }, []);

    /**
     * Internal: perform a single step submission and optional click.
     */
    const performStep = useCallback(
        async ({ classId, onUpdate }) => {
            if (!testIdRef.current) throw new Error('Test has not been started');

            // Capture screenshot
            if (!window.api || !window.api.captureScreenshot) {
                throw new Error('Window API for screenshot not available');
            }
            const screenshotBase64 = await window.api.captureScreenshot();
            const screenshotDataUri = `data:image/png;base64,${screenshotBase64}`;

            const previousStep = history[history.length - 1];
            const action_result = previousStep
                ? { clicked: !!previousStep.passed }
                : { clicked: false };

            // Submit the step
            const stepResp = await submitTestStep({
                test_id: testIdRef.current,
                class_id: classId,
                screenshot: screenshotDataUri,
                action_result,
            });

            // Store the latest response for this class_id (for retries/backfills)
            lastStepResponsesRef.current[classId] = stepResp;

            const stepResult = stepResp.step_result;
            pushHistory(stepResult);

            if (onUpdate) {
                onUpdate({
                    step_result: stepResult,
                    next_step: stepResp.next_step,
                    status: stepResp.status,
                });
            }

            // Determine click coordinates: override if present, else from next_step or detection
            let coords = null;
            if (overrideClicksRef.current[classId]) {
                coords = overrideClicksRef.current[classId];
            } else if (stepResp.next_step?.coordinates) {
                coords = stepResp.next_step.coordinates;
            } else if (stepResult.detection) {
                coords = {
                    x: stepResult.detection.click_x,
                    y: stepResult.detection.click_y,
                };
            }

            if (stepResult.passed && coords && window.api && window.api.performClick) {
                await window.api.performClick(classId,coords.x, coords.y);
            }

            return stepResp;
        },
        [history, pushHistory]
    );

    /**
     * Starts the overall flow. Accepts parameters for gameUrl/testType.
     * onUpdate is invoked per-step with { step_result, next_step, status }.
     */
    const run = useCallback(
        async ({ gameUrl, testType = 'Regression' }, onUpdate) => {
            reset();
            setIsRunning(true);
            try {
                // 1. Start test
                let startResp;
                if (testType === 'Regression') {
                    startResp = await startRegressionTest(gameUrl);
                } else {
                    startResp = await submitComplianceTest(gameUrl, testType);
                }

                const test_id = startResp.test_id;
                testIdRef.current = test_id;

                let nextStep = startResp.next_step;
                let classId = nextStep?.class_id ?? null;
                setCurrentClassId(classId);

                // Loop until completion or cancellation
                while (!cancelRef.current) {
                    if (classId === null) {
                        throw new Error('Backend did not provide next class_id');
                    }

                    // Attempt this step (with limited implicit retries inside performStep if needed upstream)
                    const stepResp = await performStep({ classId, onUpdate });

                    // If complete, break
                    if (stepResp.status === 'complete') {
                        setFinalResult(stepResp.final_result || { status: 'complete' });
                        setIsRunning(false);
                        return {
                            test_id,
                            final_result: stepResp.final_result,
                            history: [...history, stepResp.step_result],
                        };
                    }

                    // Advance to next class_id
                    classId = stepResp.next_step?.class_id ?? null;
                    setCurrentClassId(classId);
                    if (classId === null) {
                        throw new Error('Flow terminated unexpectedly without completion');
                    }
                }

                if (cancelRef.current) {
                    setError(new Error('Test was cancelled'));
                    setIsRunning(false);
                }
            } catch (err) {
                setError(err);
                setIsRunning(false);
                throw err;
            }
        },
        [history, performStep, reset]
    );

    /**
     * External trigger: retry a specific failed class_id step.
     * Re-submits the step using a fresh screenshot and the same class_id.
     */
    const retryStep = useCallback(
        async (classId, onUpdate) => {
            if (!testIdRef.current) throw new Error('Test has not been started');
            // Only allow retry if that step exists in history
            const existing = history.find((h) => h.class_id === classId);
            if (!existing) {
                throw new Error(`Cannot retry class_id ${classId} because it has not been executed yet`);
            }

            // Re-perform that step
            const stepResp = await performStep({ classId, onUpdate });
            // If this was the currentClassId, keep it; otherwise, we don’t auto-advance here
            return stepResp;
        },
        [history, performStep]
    );

    /**
     * Override click coordinates for a given class_id.
     * These coords will be used instead of detection/next_step coordinates when performing click.
     */
    const overrideClickCoords = useCallback((classId, x, y) => {
        overrideClicksRef.current[classId] = { x, y };
    }, []);

    const cancel = useCallback(() => {
        cancelRef.current = true;
    }, []);

    return {
        run, // main entrypoint
        retryStep, // external retry trigger
        overrideClickCoords, // manual click override
        cancel,
        isRunning,
        currentClassId,
        history,
        finalResult,
        error,
        reset,
    };
};
