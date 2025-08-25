import hashlib
import time
import logging
import asyncio
from typing import Dict, Any, List
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

logger = logging.getLogger(__name__)

def make_stable_test_id(test_type: str, game_url: str, timestamp: float) -> str:
    base = f"{test_type}|{game_url}|{timestamp}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"


class MaxBetLimitService(BaseTestService):
    """Service for Max Bet Limit Testing compliance testing"""
    
    def __init__(self):
        super().__init__("Max Bet Limit Testing")
    
    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Validate Max Bet Limit test request"""
        # Add specific validation logic for max bet limit tests
        return True
    
    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute Max Bet Limit Testing compliance test"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting Max Bet Limit Testing for URL: {request.game_url}")
            
            selected_tests: List[str] = request.additional_params.get("selectedTestCases", [])
            sub_test_id = selected_tests[0] if selected_tests else None

            test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

            if sub_test_id == 'mbl_001':
                # --- UPDATED JAVASCRIPT WITH ROBUST TEXT SEARCHING ---
                max_bet_limit_script = r"""
    console.log('Starting Max test script with robust text searching...');
    let image_data = null;
    let x, y;
    let response, target;

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
    response = await detectService(testType, 0, image_data);
    target = getTarget(response);
    x = target.click_x || 0;
    y = target.click_y || 0;
    console.log(`Detected service at (${x}, ${y})`);
    await performClick(0, x, y);

    // wait 10 seconds
    console.log(`Waiting 10 seconds`);
    await new Promise(resolve => setTimeout(resolve, 10000)); 

    // Step 2
    if (isElectron()) {
        image_data = await window.api.captureScreenshot();
    } else {
        console.log('(Browser) Screenshot capture placeholder');
    }
    response = await detectService(testType, 0, image_data);
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
    response = await detectService(testType, 15, image_data);
    target = getTarget(response);
    x = target.click_x || 0;
    y = target.click_y || 0;
    console.log(`Detected service at (${x}, ${y})`);
    await performClick(1, x, y);

    // Step 4
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
    await performClick(1, x, y);



"""

            else:
                max_bet_limit_script = "console.log('This Max bet test case is not implemented yet.');"
            
            execution_time = time.time() - start_time
            results_payload: Dict[str, Any] = {
                "script": max_bet_limit_script
            }

            return TestExecutionResponse(
                status="success",
                message=f"Max bet test prepared for URL: {request.game_url}",
                test_id=test_id,
                execution_time=execution_time,
                results=results_payload
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Max bet test failed: {str(e)}", exc_info=True)
            return TestExecutionResponse(
                status="error",
                message=f"Help File test failed: {str(e)}",
                test_id=f"max_bet_error_{hash(request.game_url) % 10000}",
                execution_time=execution_time,
                results={"error": str(e)}
            )
