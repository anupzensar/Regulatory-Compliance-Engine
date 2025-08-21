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
                    console.log('Starting Help File test script (robust click + OCR scroll)...');
                    
                    const getGameContext = () => {
                        const iframe = document.querySelector('iframe[id*="game"], iframe[name*="game"], iframe[src*="game"], iframe');
                        if (iframe && iframe.contentWindow) {
                            console.log('✅ Game iframe found. Operating within its context.', iframe);
                            return { window: iframe.contentWindow, document: iframe.contentWindow.document };
                        }
                        console.log('ℹ️ No game iframe detected. Operating in the top-level window context.');
                        return { window: window, document: document };
                    };

                    const gameContext = getGameContext();
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

                    // Step 1: Detect initial service/UI element
                    if (isElectron()) {
                        image_data = await window.api.captureScreenshot();
                    }
                    let response = await detectService(testType, 0, image_data);
                    let target = getTarget(response);
                    x = target.click_x || 0;
                    y = target.click_y || 0;
                    console.log(`Detected service at (${x}, ${y})`);
                    await performClick(0, x, y);

                    // Targets to search in help content
                    const TARGETS = [
                        'some settings or features may not be available in the game',
                        'any changes to game rules will be conducted in accordance with regulatory requirements'
                    ];

                    // 1) Try DOM-based click on the Help link
                    const waitAndClickHelpLink = async (context, timeout = 30000, interval = 1000) => {
                        console.log('Attempting to find and click Help link via DOM...');
                        const start = Date.now();
                        while (Date.now() - start < timeout) {
                            const container = context.document.getElementById('titan-infobar-helpTextLink');
                            if (container && container.querySelector('span')) {
                                const span = container.querySelector('span');
                                console.log('[+] Help link span found, attempting click...');
                                span.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                await new Promise(r => setTimeout(r, 200));
                                try { span.click(); return true; } catch (e) {
                                    try {
                                        const ev = new MouseEvent('click', { view: context.window, bubbles: true, cancelable: true });
                                        span.dispatchEvent(ev);
                                        return true;
                                    } catch (e2) {}
                                }
                            }
                            await new Promise(r => setTimeout(r, interval));
                        }
                        console.warn('⏱ Help link not found via DOM within timeout.');
                        return false;
                    };
                    const domClickSucceeded = await waitAndClickHelpLink(gameContext);

                    // 2) If DOM fails, fallback to OCR-based click
                    if (!domClickSucceeded) {
                        console.log('DOM help click failed, trying OCR-based click...');
                        if (isElectron()) {
                            image_data = await window.api.captureScreenshot();
                        }
                        let helpResult = await findTextInImage(image_data, 'Help');
                        
                        helpResult = await findTextInImage(image_data, "Help");
                        
                        if (helpResult?.found) {
                            x = helpResult.best.x || 0; y = helpResult.best.y || 0;
                            console.log(`OCR: Detected help at (${x}, ${y})`);
                            await performClick(1, x, y);
                        } else {
                            console.warn('Help not detected via OCR');
                        }
                    }

                    // 3) Wait for help to load
                    console.log('Waiting for help content to load...');
                    await new Promise(resolve => setTimeout(resolve, 8000));

                    // 4) Scroll-and-scan loop
                    async function searchTargetsInImage(b64, targets) {
                        const flags = {};
                        targets.forEach(t => flags[t] = false);
                        for (const t of targets) {
                            const r = await findTextInImage(b64, t);
                            if (r?.found) { flags[t] = true; }
                        }
                        return flags;
                    }
                    const mergeFlags = (a, b) => ({...a, ...Object.fromEntries(Object.entries(b).map(([k, v]) => [k, a[k] || v])) });
                    const allFound = (flags) => Object.values(flags).every(Boolean);

                    let aggregated = {}; TARGETS.forEach(t => aggregated[t] = false);
                    const maxScrolls = 12;

                    for (let i = 0; i < maxScrolls && !allFound(aggregated); i++) {
                        // CAPTURE: One screenshot is taken at the start of each scroll cycle.
                        if (isElectron()) {
                            image_data = await window.api.captureScreenshot();
                        }
                        const flags = await searchTargetsInImage(image_data, TARGETS);
                        aggregated = mergeFlags(aggregated, flags);
                        console.log(`Scan ${i + 1}/${maxScrolls} →`, aggregated);

                        if (allFound(aggregated)) {
                             console.log('✅ All targets found!');
                             break;
                        }

                        
                        let hasScrolled = false;
                        
                        // 1. Get current scroll positions of window and any inner elements
                        const scrollPositionsBefore = new Map();
                        const selectors = ['.help-content', '.help-container', '.modal-content', '.popup-content', '.scrollable', '[data-scrollable="true"]', '.help-text-container', '.help-body'];
                        const scrollableElements = [];

                        scrollPositionsBefore.set(gameContext.window, gameContext.window.scrollY);
                        for (const sel of selectors) {
                            const el = gameContext.document.querySelector(sel);
                            if (el && el.scrollHeight > el.clientHeight) {
                                scrollableElements.push(el);
                                scrollPositionsBefore.set(el, el.scrollTop);
                            }
                        }
                        
                        // 2. Attempt to scroll everything
                        gameContext.window.scrollBy(0, Math.floor(gameContext.window.innerHeight * 0.85));
                        scrollableElements.forEach(el => {
                            el.scrollTop += Math.floor(el.clientHeight * 0.85);
                        });

                        await new Promise(r => setTimeout(r, 1500)); // Wait for scroll to render

                        // 3. Check if anything actually scrolled
                        if (gameContext.window.scrollY > scrollPositionsBefore.get(gameContext.window)) {
                            hasScrolled = true;
                        }
                        for(const el of scrollableElements) {
                            if (el.scrollTop > scrollPositionsBefore.get(el)) {
                                hasScrolled = true;
                                break;
                            }
                        }

                        // 4. If no scroll occurred, we are at the end. Stop the loop.
                        if (!hasScrolled) {
                            console.log('🛑 Scroll position has not changed. End of content reached.');
                            break;
                        }
                        // ===========================================================================
                    }
                    
                    console.log('=== Help File Compliance Check Summary ===');
                    for (const t of TARGETS) {
                        console.log(`'${t}' → ${aggregated[t] ? 'FOUND ✅' : 'NOT FOUND ❌'}`);
                    }
                    console.log('Help file test completed.');
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