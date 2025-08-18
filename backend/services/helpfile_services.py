# filepath: services/helpfile_services.py
import time
import logging
import asyncio
import hashlib
from typing import Dict, Any
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD = 0.5


def make_stable_test_id(test_type: str, game_url: str, timestamp: float) -> str:
    base = f"{test_type}|{game_url}|{timestamp}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"


class HelpFileService(BaseTestService):
    """Service for Help File compliance testing"""
    
    def __init__(self):
        super().__init__("Help-File")
    
    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Validate Help File test request"""
        # Add specific validation logic for help file tests
        return True
    
    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute Help File compliance test"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting Help File test for URL: {request.game_url}")
            
            execution_time = time.time() - start_time
            test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

            # Get array of testcases
            sub_test_id = request.additional_params.get("selectedTestCases", [None])[0]

            if sub_test_id == 'hf_001':
                help_file_script = r"""
                    console.log('Starting Help File test script...');
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

                    // Step 1: Click on Continue button/icon
                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    } else {
                        console.log('(Browser) Screenshot capture placeholder');
                    }
                    let response = await detectService(testType, 0, image_data);
                    let target = getTarget(response);
                    x = target.click_x || 0;
                    y = target.click_y || 0;
                    console.log(`Detected Continue button at (${x}, ${y})`);
                    await performClick(0, x, y);


                    //click on the help button : 
                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    } else {
                        console.log('(Browser) Screenshot capture placeholder');
                    }
                    let result = await findTextInImage(image_data, "Continue");

                    x = result.best.x || 0;
                    y = result.best.y || 0;
                    console.log(`Detected help button at (${x}, ${y})`);
                    await performClick(0, x, y);

                    // Wait for help file to load
                    console.log('Waiting 10 seconds for help file to load...');
                    await new Promise(resolve => setTimeout(resolve, 10000));

                    // Function to capture help file content with scrolling
                    const captureHelpFileContent = async () => {
                        console.log('Capturing help file content...');
                        
                        // Try to find and click the help text link if available
                        if (typeof window !== 'undefined' && window.document) {
                            try {
                                const container = document.getElementById('titan-infobar-helpTextLink');
                                if (container) {
                                    const span = container.querySelector('span');
                                    if (span) {
                                        console.log('[+] Help text link found, attempting click...');
                                        span.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                        setTimeout(() => {
                                            span.click();
                                            console.log('→ Help text link clicked.');
                                        }, 200);
                                    }
                                }
                            } catch (e) {
                                console.log('Help text link interaction failed:', e);
                            }
                        }

                        // Wait a bit more for content to load
                        await new Promise(resolve => setTimeout(resolve, 2000));

                        // Capture initial screenshot
                        if (isElectron()) {
                            image_data = await window.api.captureScreenshot();
                        } else {
                            console.log('(Browser) Screenshot capture placeholder');
                        }

                        // Check for disclaimer text
                        console.log('Checking for disclaimer text...');
                        let disclaimerResult = await findTextInImage(image_data, 'some settings or features may not be available in the game');
                        
                        if (disclaimerResult.found) {
                            console.log(`🟢 Found disclaimer text: "${disclaimerResult.best.text}" at (${disclaimerResult.best.x}, ${disclaimerResult.best.y})`);
                        } else {
                            console.log('🧐 Disclaimer text not found in initial view.');
                        }

                        // Check for UK RTS requirement text
                        console.log('Checking for UK RTS requirement text...');
                        let rtsResult = await findTextInImage(image_data, 'Any changes to game rules will be conducted in accordance with regulatory requirements');
                        
                        if (rtsResult.found) {
                            console.log(`🟢 Found UK RTS text: "${rtsResult.best.text}" at (${rtsResult.best.x}, ${rtsResult.best.y})`);
                        } else {
                            console.log('🧐 UK RTS text not found in initial view.');
                        }

                        // If texts not found, try scrolling and capturing more content
                        if (!disclaimerResult.found || !rtsResult.found) {
                            console.log('Some required text not found. Attempting to scroll and capture more content...');
                            
                            // Try to scroll down to see more content
                            if (typeof window !== 'undefined' && window.document) {
                                try {
                                    // Scroll down to see more content
                                    window.scrollBy(0, 500);
                                    await new Promise(resolve => setTimeout(resolve, 1000));
                                    
                                    // Capture screenshot after scroll
                                    if (isElectron()) {
                                        image_data = await window.api.captureScreenshot();
                                    } else {
                                        console.log('(Browser) Screenshot capture placeholder after scroll');
                                    }

                                    // Check again for missing texts
                                    if (!disclaimerResult.found) {
                                        disclaimerResult = await findTextInImage(image_data, 'some settings or features may not be available in the game');
                                        if (disclaimerResult.found) {
                                            console.log(`🟢 Found disclaimer text after scroll: "${disclaimerResult.best.text}"`);
                                        }
                                    }

                                    if (!rtsResult.found) {
                                        rtsResult = await findTextInImage(image_data, 'Any changes to game rules will be conducted in accordance with regulatory requirements');
                                        if (rtsResult.found) {
                                            console.log(`🟢 Found UK RTS text after scroll: "${rtsResult.best.text}"`);
                                        }
                                    }

                                    // Scroll back up
                                    window.scrollBy(0, -500);
                                    
                                } catch (e) {
                                    console.log('Scrolling interaction failed:', e);
                                }
                            }
                        }

                        // Final summary
                        console.log('=== Help File Compliance Check Summary ===');
                        if (disclaimerResult.found) {
                            console.log('✅ Disclaimer text found');
                        } else {
                            console.log('❌ Disclaimer text not found');
                        }
                        
                        if (rtsResult.found) {
                            console.log('✅ UK RTS requirement text found');
                        } else {
                            console.log('❌ UK RTS requirement text not found');
                        }

                        return {
                            disclaimer_found: disclaimerResult.found,
                            rts_text_found: rtsResult.found
                        };
                    };

                    // Execute the help file content capture
                    const result = await captureHelpFileContent();
                    console.log('Help file test completed:', result);
                    """
            else:
                # Default help file script for other test cases
                help_file_script = r"""
                    console.log('Starting Help File test script...');
                    console.log('Test case not implemented yet.');
                    """

            results_payload: Dict[str, Any] = {
                "core_features_working": True,
                "no_critical_errors": True,
                "ui_elements_present": True,
                "flow_description": "Click Help -> Wait for Load -> Capture Content -> Check Compliance Text",
                "script": help_file_script
            }

            return TestExecutionResponse(
                status="success",
                message=f"Help File test prepared for URL: {request.game_url}",
                test_id=test_id,
                execution_time=execution_time,
                results=results_payload
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Help File test failed: {str(e)}")
            
            return TestExecutionResponse(
                status="error",
                message=f"Help File test failed: {str(e)}",
                test_id=f"help_file_error_{hash(request.game_url) % 10000}",
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
    