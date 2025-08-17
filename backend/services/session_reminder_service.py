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


            if(sub_test_id=='sr_001'):
                SR_script = r"""
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

                    //wait 50 second
                    console.log(`Waiting 50 seconds for session reminder popup to appear...`);
                    await new Promise(resolve => setTimeout(resolve, 60000)); // wait 50s

                    //detect content
                    console.log(`Detecting continue and exit buttons...`);

                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    } else {
                        console.log('(Browser) Screenshot capture placeholder');
                    }

                    // Try to detect "Continue" or "Exit" using OCR
                    console.log(`Detecting continue button`);
                    const result = await findTextInImage(image_data, "Continue");

                    if (result.found) {
                        console.log(`🟢 Found "${result.text}" at (${result.x}, ${result.y}) with confidence ${result.confidence}%`);
                    } else {
                        console.warn(`❌ Neither "Continue" nor "Exit" found on screen.`);
                    }  

                    console.log(`Detecting exit button`);
                    result = await findTextInImage(image_data, "Exit Game");
                   if (result.found) {
                        console.log(`🟢 Found "${result.text}" at (${result.x}, ${result.y}) with confidence ${result.confidence}%`);
                    } else {
                        console.warn(`❌ Neither "Continue" nor "Exit" found on screen.`);
                    } 
                    """
                pass
            elif(sub_test_id=='sr_002'):
                SR_script = r"""
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
                    await performClick(1, x, y);
                    """
                pass
            elif(sub_test_id=='sr_003'):
                SR_script = r"""
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
                    await performClick(1, x, y);
                    """
                pass
            elif(sub_test_id=='sr_004'):
                SR_script = r"""
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
                    await performClick(1, x, y);
                    """
                pass
           
            

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

