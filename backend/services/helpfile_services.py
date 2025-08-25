# filepath: services/helpfile_services.py
import time
import logging
import hashlib
from typing import Dict, Any, List
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

logger = logging.getLogger(__name__)

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
        return True

    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute Help File compliance test"""
        start_time = time.time()
        test_id = make_stable_test_id(self.test_type, request.game_url, start_time)

        try:
            logger.info(f"Starting Help File test for URL: {request.game_url}")

            selected_tests: List[str] = request.additional_params.get("selectedTestCases", [])
            sub_test_id = selected_tests[0] if selected_tests else None

            if sub_test_id == 'hf_001':
                # --- UPDATED JAVASCRIPT WITH ROBUST TEXT SEARCHING ---
                help_file_script = r"""
    console.log('Starting Help File test script with robust text searching...');
    
    let image_data = null;
    let x, y;
    
    // Click the "Continue" button using OCR
    //console.log('Finding "Continue" button...');
    //image_data = await captureScreenshot();
    //let helpResult = await findTextInImage(image_data, "Continue");
    //if (helpResult?.found) {
    //    x = helpResult.best.x || 0;
    //    y = helpResult.best.y || 0;
    //    console.log(`✅ Detected "Continue" at (${x}, ${y}). Clicking...`);
    //    await performClick(0, x, y);
    //} else {
    //    console.error('❌ "Continue" button not detected. Cannot proceed.');
    //    // return; 
    //}
    
    // Click the "Help" button using OCR
    console.log('Finding "Help" button...');
    image_data = await window.api.captureScreenshot();
    let cont_res = await findTextInImage(image_data, "Help");
    if (cont_res?.found) {
        x = cont_res.best.x || 0;
        y = cont_res.best.y || 0;
        console.log(`✅ Detected "Help" at (${x}, ${y}). Clicking...`);
        await performClick(1, x, y);
    } else {
        console.error('❌ "Help" button not detected. Cannot proceed.');
        return; 
    }

    console.log('Waiting 8 seconds for help content to load...');
    await new Promise(resolve => setTimeout(resolve, 8000));

    // --- NEW: Robust Text Searching Function ---
    const normalizeText = (text) => {
        return text
            .toLowerCase()
            // Correct common OCR mistakes (e.g., t0 -> to, 0 -> o)
            .replace(/\bt0\b/g, 'to')
            .replace(/0/g, 'o')
            // Remove all non-alphanumeric characters (keeps letters, numbers, and spaces)
            .replace(/[^a-z0-9\s]/g, '')
            // Replace multiple spaces with a single space
            .replace(/\s+/g, ' ').trim();
    };
    
    async function searchTargetsInImage(b64, targets) {
        const flags = {};
        targets.forEach(t => flags[t] = false);

        const res = await extractParagraphFromImage(b64);
        console.log('OCR Result:', res);
        
        if (res.found && res.paragraph) {
            const normalizedParagraph = normalizeText(res.paragraph);
            
            for (const target of targets) {
                const normalizedTarget = normalizeText(target);
                if (normalizedParagraph.includes(normalizedTarget)) {
                    flags[target] = true;
                }
            }
        }
        return flags;
    }

    const mergeFlags = (a, b) => ({ ...a, ...Object.fromEntries(Object.entries(b).map(([k, v]) => [k, a[k] || v])) });
    const allFound = (flags) => Object.values(flags).every(Boolean);

    const TARGETS = [
        'Some settings and features may not be available in this game',
        'Any changes to game rules will be conducted in accordance with regulatory requirements'
    ];

    let aggregated = {}; TARGETS.forEach(t => aggregated[t] = false);
    const maxScrolls = 5;

    for (let i = 0; i < maxScrolls; i++) {
        console.log(`--- Scan/Scroll Iteration: ${i + 1}/${maxScrolls} ---`);
        image_data = await captureScreenshot();
    
        const flags = await searchTargetsInImage(image_data, TARGETS);
        aggregated = mergeFlags(aggregated, flags);
        console.log('Scan results:', aggregated);

        if (allFound(aggregated)) {
            console.log('🎉 All targets found! Ending scroll loop.');
            break;
        }

        console.log('Scrolling down...');
        // Use the new function that targets the testWindow and returns a result
        const scrollResult = await scrollTestWindow(0.85); // Scroll by 85% of window height
        await new Promise(r => setTimeout(r, 1500)); // Wait for scroll animation to settle

        // ✅ CHECK IF SCROLLING STOPPED: Use the boolean returned by the function.
        // This is more reliable than checking scrollY from the wrong window context.
        if (!scrollResult?.didScroll && i > 0) {
            console.log('🛑 Scroll position did not change. Reached end of content.');
            break;
        }
    }

    console.log('--- Help File Compliance Check Summary ---');
    TARGETS.forEach(t => console.log(`'${t}' → ${aggregated[t] ? 'FOUND ✅' : 'NOT FOUND ❌'}`));
    console.log('Help file test completed.');
"""
            else:
                help_file_script = "console.log('This Help-File test case is not implemented yet.');"
            
            execution_time = time.time() - start_time
            results_payload: Dict[str, Any] = {
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
            logger.error(f"Help File test failed: {str(e)}", exc_info=True)
            return TestExecutionResponse(
                status="error",
                message=f"Help File test failed: {str(e)}",
                test_id=f"help_file_error_{hash(request.game_url) % 10000}",
                execution_time=execution_time,
                results={"error": str(e)}
            )