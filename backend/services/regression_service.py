import time
import logging
import asyncio
import hashlib
from typing import Dict, Any, List
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

logger = logging.getLogger(__name__)

# Regression flow as class IDs
REGRESSION_FLOW: List[int] = [0,1,1,15,7,10,11]
# Confidence threshold for considering a detection as passed
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


def make_stable_test_id(test_type: str, game_url: str, timestamp: float) -> str:
    base = f"{test_type}|{game_url}|{timestamp}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"


class RegressionService(BaseTestService):
    """Service for Regression compliance testing"""

    def __init__(self):
        super().__init__("Regression")
        # expose flow so orchestrator can read it
        self.CLASS_FLOW = REGRESSION_FLOW.copy()

    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Basic validation: require non-empty URL"""
        return bool(request.game_url and isinstance(request.game_url, str))

    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """
        For Regression, return an orchestration script to be executed in the renderer.
        Other validations (per-step detect/click) are handled by the injected script
        calling the UI Element Detection service via the standard /run-test endpoint.
        """
        start_time = time.time()
        try:
            logger.info(f"Starting Regression test for URL: {request.game_url}")

            await self._simulate_test_execution()

            execution_time = time.time() - start_time
            test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

            script = (
                """
console.log('Starting regression test script...');
let image_data = null;
let x, y;

const getTarget = (resp) => {
    const ct = resp && resp.results ? resp.results.click_targets : null;
    if (Array.isArray(ct)) {
        const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
        return t || {};
    }
    return ct || {};
};

let testType = "UI Element Detection";

// Step 1
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
let response = await detectService(testType, 0, image_data);
let target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);

// Step 2
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
response = await detectService(testType, 1, image_data);
target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);

// Step 3
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
response = await detectService(testType, 1, image_data);
target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);

// Step 4
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
response = await detectService(testType, 15, image_data);
target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);

// Step 5
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
response = await detectService(testType, 7, image_data);
target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);

// Step 6
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
response = await detectService(testType, 10, image_data);
target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);

// Step 7 
if (isElectron()) {
    image_data = await window.api.captureScreenshot();
} else {
    console.log('(Browser) Screenshot capture placeholder');
}
response = await detectService(testType, 11, image_data);
target = getTarget(response);
x = target.click_x || 0;
y = target.click_y || 0;
console.log(`Detected service at (${x}, ${y})`);
await performClick(0, x, y);
"""
            )

            return TestExecutionResponse(
                status="success",
                message=f"Regression script generated for URL: {request.game_url}",
                test_id=test_id,
                execution_time=execution_time,
                results={
                    "script": script,
                    "test_flow": self.CLASS_FLOW,
                    "flow_description": "Orchestrated regression flow using detect + clicks"
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Regression test failed: {str(e)}")
            return TestExecutionResponse(
                status="error",
                message=f"Regression test failed: {str(e)}",
                test_id=f"regression_error_{hash(request.game_url) % 10000}",
                execution_time=execution_time,
                results={"error": str(e)}
            )

    async def _simulate_test_execution(self):
        """Simulate test execution delay"""
        await asyncio.sleep(0.6)

    def validate_step(self, class_id: int, detection: Dict[str, Any], threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> bool:
        """
        Given a class_id and the detection dict for that step, decide if the step passes.
        Expects detection to contain 'confidence' and click coordinates.
        """
        if not detection:
            return False
        confidence = detection.get("confidence", 0.0)
        click_x = detection.get("click_x") or detection.get("mid_x")
        click_y = detection.get("click_y") or detection.get("mid_y")
        if confidence >= threshold and click_x is not None and click_y is not None:
            return True
        return False
