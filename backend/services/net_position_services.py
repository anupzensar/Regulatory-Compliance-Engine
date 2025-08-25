# # filepath: services/net_position_services.py
# import hashlib
# import time
# import logging
# import asyncio
# from typing import Dict, Any
# from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

# logger = logging.getLogger(__name__)

# DEFAULT_CONFIDENCE_THRESHOLD = 0.5


# def make_stable_test_id(test_type: str, game_url: str, timestamp: float) -> str:
#     base = f"{test_type}|{game_url}|{timestamp}"
#     digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
#     return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"


# class NetPositionService(BaseTestService):
#     """Service for Net Position compliance testing"""

#     def __init__(self):
#         super().__init__("Net Position")

#     def validate_request(self, request: TestExecutionRequest) -> bool:
#         """Validate Net Position test request"""
#         return True

#     async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
#         """Execute Net Position compliance test"""
#         start_time = time.time()

#         try:
#             logger.info(f"Starting Net Position test for URL: {request.game_url}")
#             test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

#             sub_test_id = request.additional_params["selectedTestCases"][0]

#             # ---------------- SR_001 ----------------
#             if sub_test_id == "sr_001":
#                 NP_script = r"""
#                     console.log('Starting Net Position sr_001 test...');
                    
#                     async function extractNetPosition(b64img) {
#                         const res = await extractParagraphFromImage2(b64img);
#                         console.log('OCR Result:', res);

#                         if (!res?.paragraph) return null;
#                         const text = res.paragraph;
#                         const regex = /Net\s*position[:\s]*£?([\d,]+(\.\d+)?)/i;
#                         const match = text.match(regex);

#                         if (match) {
#                             console.log("✅ Found Net Position:", match[1]);
#                             return match[1].replace(',', '');
#                         }
#                         console.log("❌ Net Position not found.");
#                         return null;
#                     }

#                     const getTarget = (resp) => {
#                         const ct = resp && resp.results ? resp.results.click_targets : null;
#                         if (Array.isArray(ct)) {
#                             const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
#                             return t || {};
#                         }
#                         return ct || {};
#                     };
                    
#                     let image_data = null;
#                     let x = 0, y = 0;
#                     let testType = "UI Element Detection";
                    
#                     if (isElectron()) {
#                         image_data = await window.api.captureScreenshot();
#                     } else {
#                         console.log('(Browser) Screenshot capture placeholder');
#                     }

#                     let response = await detectService(testType, 0, image_data);
#                     let target = getTarget(response);
#                     x = target.click_x || 0;
#                     y = target.click_y || 0;
#                     console.log(`Detected service at (${x}, ${y})`);
#                     await performClick(0, x, y);
                    
#                     await new Promise(r => setTimeout(r, 3000));

#                     // Extract Net Position
#                     image_data = await window.api.captureScreenshot();
#                     let netValue = await extractNetPosition(image_data);

#                     await new Promise(r => setTimeout(r, 5000));

#                     // Verify Net Position == 0.00
#                     image_data = await window.api.captureScreenshot();
#                     let finalValue = await extractNetPosition(image_data);
#                     if (finalValue === "0.00") {
#                         console.log("🎉 Test Passed! Net Position is 0.00");
#                     } else {
#                         console.error(`❌ Test Failed. Expected 0.00 but got ${finalValue}`);
#                     }
#                 """

#             # ---------------- SR_002 ----------------
#             elif sub_test_id == "sr_002":
#                 NP_script = r"""
#                     console.log('Starting Net Position sr_002 test...');
                    
#                     async function extractNetPosition(b64img) {
#                         const res = await extractParagraphFromImage2(b64img);
#                         console.log('OCR Result:', res);

#                         if (!res?.paragraph) return null;
#                         const text = res.paragraph;
#                         const regex = /Net\s*position[:\s]*£?([\d,]+(\.\d+)?)/i;
#                         const match = text.match(regex);

#                         if (match) {
#                             console.log("✅ Found Net Position:", match[1]);
#                             return match[1].replace(',', '');
#                         }
#                         console.log("❌ Net Position not found.");
#                         return null;
#                     }

#                     const getTarget = (resp) => {
#                         const ct = resp && resp.results ? resp.results.click_targets : null;
#                         if (Array.isArray(ct)) {
#                             const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
#                             return t || {};
#                         }
#                         return ct || {};
#                     };
                    
#                     let image_data = null;
#                     let x = 0, y = 0;
#                     let testType = "UI Element Detection";
                    
#                     if (isElectron()) {
#                         image_data = await window.api.captureScreenshot();
#                     } else {
#                         console.log('(Browser) Screenshot capture placeholder');
#                     }

#                     let response = await detectService(testType, 0, image_data);
#                     let target = getTarget(response);
#                     x = target.click_x || 0;
#                     y = target.click_y || 0;
#                     console.log(`Detected service at (${x}, ${y})`);
#                     await performClick(0, x, y);

#                     await new Promise(r => setTimeout(r, 3000));

#                     // Extract Net Position
#                     image_data = await window.api.captureScreenshot();
#                     let netValue = await extractNetPosition(image_data);

#                     // Spin the game
#                     image_data = await window.api.captureScreenshot();
#                     response = await detectService(testType, 1, image_data);
#                     target = getTarget(response);
#                     x = target.click_x || 0;
#                     y = target.click_y || 0;
#                     console.log(`Detected service at (${x}, ${y})`);
#                     if (x && y) { await performClick(1, x, y); } else { console.warn('Skip click: no coords for spin'); }

#                     await new Promise(r => setTimeout(r, 5000));

#                     // Verify Net Position == 0.00
#                     image_data = await window.api.captureScreenshot();
#                     let finalValue = await extractNetPosition(image_data);
#                     if (finalValue === "0.00") {
#                         console.log("🎉 Test Passed! Net Position is 0.00");
#                     } else {
#                         console.error(`❌ Test Failed. Expected 0.00 but got ${finalValue}`);
#                     }
#                 """

#             # ---------------- SR_003 ----------------
#             elif sub_test_id == "sr_003":
#                 NP_script = r"""
#                     console.log('Starting Net Position sr_003 test...');
                    
#                     async function extractNetPosition(b64img) {
#                         const res = await extractParagraphFromImage2(b64img);
#                         console.log('OCR Result:', res);

#                         if (!res?.paragraph) return null;
#                         const text = res.paragraph;
#                         const regex = /Net\s*position[:\s]*£?([\d,]+(\.\d+)?)/i;
#                         const match = text.match(regex);

#                         if (match) {
#                             console.log("✅ Found Net Position:", match[1]);
#                             return match[1].replace(',', '');
#                         }
#                         console.log("❌ Net Position not found.");
#                         return null;
#                     }

#                     const getTarget = (resp) => {
#                         const ct = resp && resp.results ? resp.results.click_targets : null;
#                         if (Array.isArray(ct)) {
#                             const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
#                             return t || {};
#                         }
#                         return ct || {};
#                     };
                    
#                     let image_data = null;
#                     let x = 0, y = 0;
#                     let testType = "UI Element Detection";
                    
#                     if (isElectron()) {
#                         image_data = await window.api.captureScreenshot();
#                     } else {
#                         console.log('(Browser) Screenshot capture placeholder');
#                     }

#                     let response = await detectService(testType, 0, image_data);
#                     let target = getTarget(response);
#                     x = target.click_x || 0;
#                     y = target.click_y || 0;
#                     console.log(`Detected service at (${x}, ${y})`);
#                     await performClick(0, x, y);

#                     await new Promise(r => setTimeout(r, 3000));

#                     // Extract Net Position
#                     image_data = await window.api.captureScreenshot();
#                     let netValue = await extractNetPosition(image_data);

#                     // Spin the game
#                     image_data = await window.api.captureScreenshot();
#                     response = await detectService(testType, 1, image_data);
#                     target = getTarget(response);
#                     x = target.click_x || 0;
#                     y = target.click_y || 0;
#                     console.log(`Detected service at (${x}, ${y})`);
#                     if (x && y) { await performClick(1, x, y); } else { console.warn('Skip click: no coords for spin'); }

#                     await new Promise(r => setTimeout(r, 5000));

#                     // Verify Net Position == 2.80
#                     image_data = await window.api.captureScreenshot();
#                     let finalValue = await extractNetPosition(image_data);
#                     if (finalValue === "2.80") {
#                         console.log("🎉 Test Passed! Net Position is 2.80");
#                     } else {
#                         console.error(`❌ Test Failed. Expected 2.80 but got ${finalValue}`);
#                     }
#                 """
#             else:
#                 NP_script = "console.log('❌ This Net Position test case is not implemented yet.');"

#             # Final payload
#             execution_time = time.time() - start_time
#             results_payload: Dict[str, Any] = {
#                 "script": NP_script,
#                 "flow_description": "Load Game -> Continue -> Extract Net Position -> Spin -> Verify Net Position"
#             }

#             return TestExecutionResponse(
#                 status="success",
#                 message=f"Net Position test prepared for URL: {request.game_url}",
#                 test_id=test_id,
#                 execution_time=execution_time,
#                 results=results_payload
#             )

#         except Exception as e:
#             execution_time = time.time() - start_time
#             logger.error(f"Net Position test failed: {str(e)}")

#             return TestExecutionResponse(
#                 status="error",
#                 message=f"Net Position test failed: {str(e)}",
#                 test_id=f"net_position_error_{hash(request.game_url) % 10000}",
#                 execution_time=execution_time,
#                 results={"error": str(e)}
#             )

#     async def _simulate_test_execution(self):
#         """Simulate test execution delay"""
#         await asyncio.sleep(0.5)

#     def validate_step(self, class_id: int, detection: Dict[str, Any], threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> bool:
#         """
#         Given a class_id and the detection dict for that step, decide if the step passes.
#         """
#         if not detection:
#             return False
#         confidence = detection.get("confidence", 0.0)
#         click_x = detection.get("click_x") or detection.get("mid_x")
#         click_y = detection.get("click_y") or detection.get("mid_y")
#         if confidence >= threshold and click_x is not None and click_y is not None:
#             return True
#         return False


# filepath: services/net_position_services.py
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


class NetPositionService(BaseTestService):
    """Service for Net Position compliance testing"""

    def __init__(self):
        super().__init__("Net Position")

    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Validate Net Position test request"""
        return True

    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute Net Position compliance test"""
        start_time = time.time()

        try:
            logger.info(f"Starting Net Position test for URL: {request.game_url}")
            test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

            sub_test_id = request.additional_params["selectedTestCases"][0]

            # ---------------- SR_001 ----------------
            if sub_test_id == "sr_001":
                NP_script = r"""
                    console.log('Starting Net Position sr_001 test...');
                    
                    async function extractNetPosition(b64img) {
                        const res = await extractParagraphFromImage2(b64img);
                        console.log('OCR Result:', res);

                        if (!res?.paragraph) return null;
                        const text = res.paragraph;
                        
                        // More specific regex to ensure decimal point is captured correctly
                        const regex = /Net\s*position[:\s]*[^\d\r\n-]*([\dO,]+\.[\dO]{2})/i;
                        const match = text.match(regex);

                        if (match && match[1]) {
                            // Clean up common OCR errors (e.g., 'O' for '0', remove commas)
                            const cleanedValue = match[1].replace(/O/gi, '0').replace(/,/g, '');
                            console.log("✅ Found Net Position:", cleanedValue);
                            return cleanedValue;
                        }
                        console.log("❌ Net Position not found.");
                        return null;
                    }

                    const getTarget = (resp) => {
                        const ct = resp && resp.results ? resp.results.click_targets : null;
                        if (Array.isArray(ct)) {
                            const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
                            return t || {};
                        }
                        return ct || {};
                    };
                    
                    let image_data = null;
                    let x = 0, y = 0;
                    let testType = "UI Element Detection";
                    
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
                    
                    await new Promise(r => setTimeout(r, 3000));

                    // Extract Net Position
                    image_data = await window.api.captureScreenshot();
                    let netValue = await extractNetPosition(image_data);

                    await new Promise(r => setTimeout(r, 5000));

                    // Verify Net Position == 0.00
                    image_data = await window.api.captureScreenshot();
                    let finalValue = await extractNetPosition(image_data);
                    if (finalValue === "0.00") {
                        console.log("🎉 Test Passed! Net Position is 0.00");
                    } else {
                        console.error(`❌ Test Failed. Expected 0.00 but got ${finalValue}`);
                    }
                """

            # ---------------- SR_002 ----------------
            elif sub_test_id == "sr_002":
                NP_script = r"""
                    console.log('Starting Net Position sr_002 test...');
                    
                    async function extractNetPosition(b64img) {
                        const res = await extractParagraphFromImage2(b64img);
                        console.log('OCR Result:', res);

                        if (!res?.paragraph) return null;
                        const text = res.paragraph;
                        
                        // More specific regex to ensure decimal point is captured correctly
                        const regex = /Net\s*position[:\s]*[^\d\r\n-]*([\dO,]+\.[\dO]{2})/i;
                        const match = text.match(regex);

                        if (match && match[1]) {
                            // Clean up common OCR errors (e.g., 'O' for '0', remove commas)
                            const cleanedValue = match[1].replace(/O/gi, '0').replace(/,/g, '');
                            console.log("✅ Found Net Position:", cleanedValue);
                            return cleanedValue;
                        }
                        console.log("❌ Net Position not found.");
                        return null;
                    }

                    const getTarget = (resp) => {
                        const ct = resp && resp.results ? resp.results.click_targets : null;
                        if (Array.isArray(ct)) {
                            const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
                            return t || {};
                        }
                        return ct || {};
                    };
                    
                    let image_data = null;
                    let x = 0, y = 0;
                    let testType = "UI Element Detection";
                    
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

                    await new Promise(r => setTimeout(r, 3000));

                    // Extract Net Position
                    image_data = await window.api.captureScreenshot();
                    let netValue = await extractNetPosition(image_data);

                    // Spin the game
                    image_data = await window.api.captureScreenshot();
                    response = await detectService(testType, 1, image_data);
                    target = getTarget(response);
                    x = target.click_x || 0;
                    y = target.click_y || 0;
                    console.log(`Detected service at (${x}, ${y})`);
                    if (x && y) { await performClick(1, x, y); } else { console.warn('Skip click: no coords for spin'); }

                    await new Promise(r => setTimeout(r, 5000));

                    // Verify Net Position == 0.00
                    image_data = await window.api.captureScreenshot();
                    let finalValue = await extractNetPosition(image_data);
                    if (finalValue === "0.00") {
                        console.log("🎉 Test Passed! Net Position is 0.00");
                    } else {
                        console.error(`❌ Test Failed. Expected 0.00 but got ${finalValue}`);
                    }
                """

            # ---------------- SR_003 ----------------
            elif sub_test_id == "sr_003":
                NP_script = r"""
                    console.log('Starting Net Position sr_003 test...');
                    
                    async function extractNetPosition(b64img) {
                        const res = await extractParagraphFromImage2(b64img);
                        console.log('OCR Result:', res);

                        if (!res?.paragraph) return null;
                        const text = res.paragraph;
                        
                        // More specific regex to ensure decimal point is captured correctly
                        const regex = /Net\s*position[:\s]*[^\d\r\n-]*([\dO,]+\.[\dO]{2})/i;
                        const match = text.match(regex);

                        if (match && match[1]) {
                            // Clean up common OCR errors (e.g., 'O' for '0', remove commas)
                            const cleanedValue = match[1].replace(/O/gi, '0').replace(/,/g, '');
                            console.log("✅ Found Net Position:", cleanedValue);
                            return cleanedValue;
                        }
                        console.log("❌ Net Position not found.");
                        return null;
                    }

                    const getTarget = (resp) => {
                        const ct = resp && resp.results ? resp.results.click_targets : null;
                        if (Array.isArray(ct)) {
                            const t = ct.find(t => t && t.click_x != null && t.click_y != null) || ct[0];
                            return t || {};
                        }
                        return ct || {};
                    };
                    
                    let image_data = null;
                    let x = 0, y = 0;
                    let testType = "UI Element Detection";
                    
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

                    await new Promise(r => setTimeout(r, 3000));

                    // Extract Net Position
                    image_data = await window.api.captureScreenshot();
                    let netValue = await extractNetPosition(image_data);

                    // Spin the game
                    image_data = await window.api.captureScreenshot();
                    response = await detectService(testType, 1, image_data);
                    target = getTarget(response);
                    x = target.click_x || 0;
                    y = target.click_y || 0;
                    console.log(`Detected service at (${x}, ${y})`);
                    if (x && y) { await performClick(1, x, y); } else { console.warn('Skip click: no coords for spin'); }

                    await new Promise(r => setTimeout(r, 10000));

                    // Verify Net Position == 2.80
                    image_data = await window.api.captureScreenshot();
                    let finalValue = await extractNetPosition(image_data);
                    if (finalValue === "2.80") {
                        console.log("🎉 Test Passed! Net Position is 2.80");
                    } else {
                        console.error(`❌ Test Failed. Expected 2.80 but got ${finalValue}`);
                    }
                """
            else:
                NP_script = "console.log('❌ This Net Position test case is not implemented yet.');"

            # Final payload
            execution_time = time.time() - start_time
            results_payload: Dict[str, Any] = {
                "script": NP_script,
                "flow_description": "Load Game -> Continue -> Extract Net Position -> Spin -> Verify Net Position"
            }

            return TestExecutionResponse(
                status="success",
                message=f"Net Position test prepared for URL: {request.game_url}",
                test_id=test_id,
                execution_time=execution_time,
                results=results_payload
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Net Position test failed: {str(e)}")

            return TestExecutionResponse(
                status="error",
                message=f"Net Position test failed: {str(e)}",
                test_id=f"net_position_error_{hash(request.game_url) % 10000}",
                execution_time=execution_time,
                results={"error": str(e)}
            )

    async def _simulate_test_execution(self):
        """Simulate test execution delay"""
        await asyncio.sleep(0.5)

    def validate_step(self, class_id: int, detection: Dict[str, Any], threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> bool:
        """
        Given a class_id and the detection dict for that step, decide if the step passes.
        """
        if not detection:
            return False
        confidence = detection.get("confidence", 0.0)
        click_x = detection.get("click_x") or detection.get("mid_x")
        click_y = detection.get("click_y") or detection.get("mid_y")
        if confidence >= threshold and click_x is not None and click_y is not None:
            return True
        return False