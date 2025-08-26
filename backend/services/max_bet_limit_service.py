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

    // Helper: Crop 10% top and 10% bottom from base64 image
    async function cropImageBase64(b64img) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = function () {
                const canvas = document.createElement("canvas");
                const ctx = canvas.getContext("2d");

                const cropTop = img.height * 0.1;   // 10% top
                const cropBottom = img.height * 0.1; // 10% bottom
                const cropHeight = img.height - cropTop - cropBottom;

                canvas.width = img.width;
                canvas.height = cropHeight;

                // Draw only the middle 80% portion
                ctx.drawImage(img, 0, cropTop, img.width, cropHeight, 0, 0, img.width, cropHeight);

                resolve(canvas.toDataURL("image/png")); // returns cropped base64
            };
            img.onerror = reject;

            
            if (!b64img.startsWith("data:image")) {
                img.src = "data:image/png;base64," + b64img;
            } else {
                img.src = b64img;
            }
        });
    }
    function getBase64Data(imgBase64) {
    // remove "data:image/...;base64," part
    return imgBase64.replace(/^data:image\/\w+;base64,/, "");
    }
    
    function extractMaxCurrency(ocrText) {
        if (!ocrText) return null;

        // Step 1: Normalize OCR errors (replace 'O' with '0' when in numeric context)
        let normalized = ocrText.replace(/([0-9])O([0-9])/g, "$10$2"); // in middle of digits
        normalized = normalized.replace(/O(?=\d)/g, "0");              // 'O' at start of number
        normalized = normalized.replace(/(?<=\d)O/g, "0");              // 'O' at end of number

        // Step 2: Extract numbers like 2.00, 0.80 etc.
        let matches = normalized.match(/\d+\.\d{2}/g);

        if (!matches) return null;

        // Step 3: Convert to numbers
        let numbers = matches.map(n => parseFloat(n));

        // Step 4: Return max
        return Math.max(...numbers);
    }



    async function extractNetPosition(b64img) {
        try {
            // crop 10% top & bottom before OCR
            const croppedImg = await cropImageBase64(b64img);
            
            console.log("b64img" , b64img);
            const base64Data = getBase64Data(croppedImg);
            console.log("croppedImg" , base64Data);
            

            const res = await extractParagraphFromImage2(base64Data);
            console.log("OCR Result:", res);

            if (!res?.paragraph) return null;
            const text = res.paragraph;
            console.log("OCR Text:", text);

            return text;
        } catch (err) {
            console.error("Cropping/OCR failed:", err);
            return null;
        }
    }

    if (isElectron()) {
        image_data = await window.api.captureScreenshot();
    } else {
        console.log('(Browser) Screenshot capture placeholder');
    }
    const maxbet = await extractNetPosition(image_data);
    
    const num = extractMaxCurrency(maxbet);

    if (num <= 6.25) { 
        console.log("🎉 Test Passed! max bet is less than or equal to 6.25: " + num + "  ");
    } else {
        console.error(`❌ Test Failed. max bet is greater than 6.25: ${num} `);
    }

    
    
"""

            if sub_test_id == 'mbl_002':
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

    // Helper: Crop 10% top and 10% bottom from base64 image
    async function cropImageBase64(b64img) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = function () {
                const canvas = document.createElement("canvas");
                const ctx = canvas.getContext("2d");

                const cropTop = img.height * 0.1;   // 10% top
                const cropBottom = img.height * 0.1; // 10% bottom
                const cropHeight = img.height - cropTop - cropBottom;

                canvas.width = img.width;
                canvas.height = cropHeight;

                // Draw only the middle 80% portion
                ctx.drawImage(img, 0, cropTop, img.width, cropHeight, 0, 0, img.width, cropHeight);

                resolve(canvas.toDataURL("image/png")); // returns cropped base64
            };
            img.onerror = reject;

            
            if (!b64img.startsWith("data:image")) {
                img.src = "data:image/png;base64," + b64img;
            } else {
                img.src = b64img;
            }
        });
    }
    function getBase64Data(imgBase64) {
    // remove "data:image/...;base64," part
    return imgBase64.replace(/^data:image\/\w+;base64,/, "");
    }
    
    function extractMaxCurrency(ocrText) {
        if (!ocrText) return null;

        // Step 1: Normalize OCR errors (replace 'O' with '0' when in numeric context)
        let normalized = ocrText.replace(/([0-9])O([0-9])/g, "$10$2"); // in middle of digits
        normalized = normalized.replace(/O(?=\d)/g, "0");              // 'O' at start of number
        normalized = normalized.replace(/(?<=\d)O/g, "0");              // 'O' at end of number

        // Step 2: Extract numbers like 2.00, 0.80 etc.
        let matches = normalized.match(/\d+\.\d{2}/g);

        if (!matches) return null;

        // Step 3: Convert to numbers
        let numbers = matches.map(n => parseFloat(n));

        // Step 4: Return max
        return Math.max(...numbers);
    }



    async function extractNetPosition(b64img) {
        try {
            // crop 10% top & bottom before OCR
            const croppedImg = await cropImageBase64(b64img);
            
            const base64Data = getBase64Data(croppedImg);
            
            const res = await extractParagraphFromImage2(base64Data);
            console.log("OCR Result:", res);

            if (!res?.paragraph) return null;
            const text = res.paragraph;
            console.log("OCR Text:", text);

            return text;
        } catch (err) {
            console.error("Cropping/OCR failed:", err);
            return null;
        }
    }

    if (isElectron()) {
        image_data = await window.api.captureScreenshot();
    } else {
        console.log('(Browser) Screenshot capture placeholder');
    }
    const maxbet = await extractNetPosition(image_data);
    
    const num = extractMaxCurrency(maxbet);

    if (num <= 5.00) { 
        console.log("🎉 Test Passed! max bet is less than or equal to 5.00: " + num + "  ");
    } else {
        console.error(`❌ Test Failed. max bet is greater than 5.00: ${num} `);
    }

    
"""
            if sub_test_id == 'mbl_003':
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

    // Helper: Crop 10% top and 10% bottom from base64 image
    async function cropImageBase64(b64img) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = function () {
                const canvas = document.createElement("canvas");
                const ctx = canvas.getContext("2d");

                const cropTop = img.height * 0.1;   // 10% top
                const cropBottom = img.height * 0.1; // 10% bottom
                const cropHeight = img.height - cropTop - cropBottom;

                canvas.width = img.width;
                canvas.height = cropHeight;

                // Draw only the middle 80% portion
                ctx.drawImage(img, 0, cropTop, img.width, cropHeight, 0, 0, img.width, cropHeight);

                resolve(canvas.toDataURL("image/png")); // returns cropped base64
            };
            img.onerror = reject;

            
            if (!b64img.startsWith("data:image")) {
                img.src = "data:image/png;base64," + b64img;
            } else {
                img.src = b64img;
            }
        });
    }
    function getBase64Data(imgBase64) {
    // remove "data:image/...;base64," part
    return imgBase64.replace(/^data:image\/\w+;base64,/, "");
    }
    
    function extractMaxCurrency(ocrText) {
        if (!ocrText) return null;

        // Step 1: Normalize OCR errors (replace 'O' with '0' when in numeric context)
        let normalized = ocrText.replace(/([0-9])O([0-9])/g, "$10$2"); // in middle of digits
        normalized = normalized.replace(/O(?=\d)/g, "0");              // 'O' at start of number
        normalized = normalized.replace(/(?<=\d)O/g, "0");              // 'O' at end of number

        // Step 2: Extract numbers like 2.00, 0.80 etc.
        let matches = normalized.match(/\d+\.\d{2}/g);

        if (!matches) return null;

        // Step 3: Convert to numbers
        let numbers = matches.map(n => parseFloat(n));

        // Step 4: Return max
        return Math.max(...numbers);
    }



    async function extractNetPosition(b64img) {
        try {
            // crop 10% top & bottom before OCR
            const croppedImg = await cropImageBase64(b64img);
            
            console.log("b64img" , b64img);
            const base64Data = getBase64Data(croppedImg);
            console.log("croppedImg" , base64Data);
            

            const res = await extractParagraphFromImage2(base64Data);
            console.log("OCR Result:", res);

            if (!res?.paragraph) return null;
            const text = res.paragraph;
            console.log("OCR Text:", text);

            return text;
        } catch (err) {
            console.error("Cropping/OCR failed:", err);
            return null;
        }
    }

    if (isElectron()) {
        image_data = await window.api.captureScreenshot();
    } else {
        console.log('(Browser) Screenshot capture placeholder');
    }
    const maxbet = await extractNetPosition(image_data);
    
    const num = extractMaxCurrency(maxbet);

    if (num <= 3.00) { 
        console.log("🎉 Test Passed! max bet is less than or equal to 3.00: " + num + "  ");
    } else {
        console.error(`❌ Test Failed. max bet is greater than 3.00: ${num} `);
    }

    
    
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