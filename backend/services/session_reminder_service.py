import hashlib
import time
import logging
import asyncio
from typing import Dict, Any
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD = 0.5


def make_stable_test_id(test_type: str, game_url: str, timestamp: float) -> str:
    base = f"{test_type}|{game_url}|{timestamp}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"


class SessionReminderService(BaseTestService):
    """Service for Session Reminder compliance testing"""

    def __init__(self):
        super().__init__("Session Reminder")

    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Validate Session Reminder test request"""
        # Add specific validation logic for session reminder tests
        return True

    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute Session Reminder compliance test"""
        start_time = time.time()

        try:
            logger.info(f"Starting Session Reminder test for URL: {request.game_url}")

            execution_time = time.time() - start_time
            test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

            # Get array of testcases
            sub_test_id = request.additional_params["selectedTestCases"][0]

            if sub_test_id == "sr_001":
                SR_script = r"""
                    console.log('Starting Session Reminder test script...');
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

                    //wait 50 second
                    console.log(`Waiting 50 seconds for session reminder popup to appear...`);
                    await new Promise(resolve => setTimeout(resolve, 60000)); // wait 50s

                    console.log("Detecting continue and exit buttons...");

                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    } else {
                        console.log("(Browser) Screenshot capture placeholder");
                    }

                    // Try to detect "Continue"
                    console.log("Detecting Continue button...");
                    let result = await findTextInImage(image_data, "Continue");

                    if (result.found) {
                        console.log(
                            `🟢 Found "${result.best.text}" at (${result.best.x}, ${result.best.y}) with confidence ${result.best.confidence}%`
                        );
                    } else {
                        console.log('🧐 "Continue" not found.');
                    }

                    // Try to detect "Exit Game"
                    console.log("Detecting Exit Game button...");
                    result = await findTextInImage(image_data, "Exit Game");

                    if (result.found) {
                        console.log(
                            `🟢 Found "${result.best.text}" at (${result.best.x}, ${result.best.y}) with confidence ${result.best.confidence}%`
                        );
                    } else {
                        console.warn('❌ "Exit Game" not found.');
                    }
                """
            elif sub_test_id == "sr_002":
                SR_script = r"""
                    console.log('Starting Session Reminder test script...');
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
                    if (x != null && y != null) { await performClick(0, x, y); } else { console.warn('Skip click: no coords'); }

                    // wait 60 seconds for the popup
                    console.log(`Waiting 60 seconds for session reminder popup to appear...`);
                    await new Promise(resolve => setTimeout(resolve, 60000));

                    console.log("Detecting continue  buttons...");

                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    } else {
                        console.log("(Browser) Screenshot capture placeholder");
                    }

                    // Try to detect "Continue"
                    console.log("Detecting Continue button...");
                    let result = await findTextInImage(image_data, "Continue");
                    if (result.found) {
                        console.log(`Continue found at (${result.best.x}, ${result.best.y}) conf ${result.best.confidence}%`);
                        
                        x = result.best.x || 0;
                        y = result.best.y || 0;
                        if (x != null && y != null) { await performClick(1, x, y); }
                        
                        // then spin the game : 
                        
                        // Step 1
                        if (isElectron()) {
                            image_data = await window.api.captureScreenshot();
                        } else {
                            console.log('(Browser) Screenshot capture placeholder');
                        }
                        let response = await detectService(testType, 1, image_data);
                        let target = getTarget(response);
                        x = target.click_x || 0;
                        y = target.click_y || 0;
                        console.log(`Detected service at (${x}, ${y})`);
                        if (x != null && y != null) { await performClick(0, x, y); } else { console.warn('Skip click: no coords for step 1'); }

                    } else {
                        console.log('"Continue" not found.');
                    }

                    // Try to detect "Exit Game"
                    //console.log("Detecting Exit Game button...");
                    //result = await findTextInImage(image_data, "Exit Game");

                    //if (result.found) {
                    //    console.log(`🟢 Found "${result.best.text}" at (${result.best.x}, ${result.best.y}) with confidence ${result.best.confidence}%`);
                    //    
                    //} else {
                    //    console.warn('❌ "Exit Game" not found.');
                    //}
                """
            elif sub_test_id == "sr_003":
                SR_script = r"""
                    console.log('Starting Session Reminder test script...');
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

                    //wait 60 second
                    console.log(`Waiting 60 seconds for session reminder popup to appear...`);
                    await new Promise(resolve => setTimeout(resolve, 60000));

                    console.log("Detecting  exit buttons...");

                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    } else {
                        console.log("(Browser) Screenshot capture placeholder");
                    }

                    // Try to detect Exit Game"
                    console.log("Detecting  Exit Game button...");
                    let result = await findTextInImage(image_data, "Exit Game");

                    if (result.found) {
                        console.log(
                            `🟢 Found "${result.best.text}" at (${result.best.x}, ${result.best.y}) with confidence ${result.best.confidence}%`
                        );

                        x = result.best.x|| 0;
                        y = result.best.y || 0;

                        await performClick(1, x, y);

                        console.log(`Waiting 20 seconds for loading the error page...`)
                        await new Promise(resolve => setTimeout(resolve, 20000));

                        if (isElectron()) {
                            image_data = await window.api.captureScreenshot();
                        } else {
                            console.log('(Browser) Screenshot capture placeholder');
                        }

                        // Try to detect Error Keyword
                        console.log("Detecting  Exit Game button...");
                        let result2 = await findTextInImage(image_data, "Error");

                        if (result2.found) {
                            console.log(
                                `🟢 Found "${result2.best.text}" at (${result2.best.x}, ${result2.best.y}) with confidence ${result2.best.confidence}%`
                            );
                        } else {
                            console.log('🧐 "Error" not found.');
                        }

                    } else {
                        console.log('🧐 "Exit Game" not found.');
                    }
                """
            elif sub_test_id == "sr_004":
                SR_script = r"""
                    console.log('Starting Session Reminder test script...');
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
                    await performClick(1, x, y);
                """

            results_payload: Dict[str, Any] = {
                "core_features_working": True,
                "no_critical_errors": True,
                "ui_elements_present": True,
                "flow_description": "Load Game -> Spin Button -> Win Animation -> Collect Button",
                "script": SR_script
            }

            return TestExecutionResponse(
                status="success",
                message=f"Regression test prepared for URL: {request.game_url}",
                test_id=test_id,
                execution_time=execution_time,
                results=results_payload
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Session Reminder test failed: {str(e)}")

            return TestExecutionResponse(
                status="error",
                message=f"Session Reminder test failed: {str(e)}",
                test_id=f"session_reminder_error_{hash(request.game_url) % 10000}",
                execution_time=execution_time,
                results={"error": str(e)}
            )

    async def _simulate_test_execution(self):
        """Simulate test execution delay"""
        # Simulate some processing time
        await asyncio.sleep(0.5)

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
