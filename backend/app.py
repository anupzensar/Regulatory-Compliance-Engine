import time
import hashlib
import base64
import logging
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from config import settings
from services.test_service_factory import test_service_factory  # adjust if your package path differs
from services.base_service import TestExecutionRequest

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger("orchestrator")

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# CORS middleware with configurable origins - supports Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ALLOWED_ORIGINS == ["*"] else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["*"],
)

# In-memory execution context store (replace with durable store in prod)
executions: Dict[str, Dict[str, Any]] = {}

# ------------------ Utilities ------------------

def make_test_id(test_type: str, game_url: str, timestamp: Optional[float] = None) -> str:
    if timestamp is None:
        timestamp = time.time()
    base = f"{test_type}|{game_url}|{timestamp}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"

def safe_decode_base64(data: str) -> bytes:
    try:
        if "," in data:
            data = data.split(",", 1)[1]
        return base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Invalid base64 data: {e}")

# ------------------ Schemas ------------------

class RunTestRequest(BaseModel):
    gameUrl: str
    testType: str

class NextStepInfo(BaseModel):
    class_id: int
    clickable: bool = True
    coordinates: Optional[Dict[str, float]] = None  # {"x": ..., "y": ...}
    instructions: str

class RunTestResponse(BaseModel):
    test_id: str
    next_step: NextStepInfo

class StepRequest(BaseModel):
    test_id: str
    class_id: int  # expected class_id for this step
    screenshot: str  # base64 encoded PNG
    action_result: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"clicked": True}

class DetectionInfo(BaseModel):
    click_x: Optional[float]
    click_y: Optional[float]
    confidence: float
    bounding_box: Optional[Dict[str, float]] = None  # x1,y1,x2,y2
    class_id: int

class StepResult(BaseModel):
    class_id: int
    passed: bool
    detection: Optional[DetectionInfo] = None

class StepResponse(BaseModel):
    status: str  # "continue", "complete", "failed"
    step_result: StepResult
    next_step: Optional[NextStepInfo] = None
    final_result: Optional[Dict[str, Any]] = None

# ------------------ Endpoint implementations ------------------

@app.get("/", response_model=dict)
def read_root():
    """Health check endpoint"""
    return {"message": "Regulatory Compliance Engine API is running", "status": "healthy"}

@app.get("/test-types", response_model=dict)
def get_test_types():
    
    """Get all available test types"""
    return {
        "test_types": test_service_factory.get_available_test_types(),
        "count": len(test_service_factory.get_available_test_types())
    }

@app.post("/run-test", response_model=RunTestResponse)
async def run_test(request: RunTestRequest):
    test_type = request.testType
    game_url = request.gameUrl

    if not test_service_factory.is_valid_test_type(test_type):
        available = test_service_factory.get_available_test_types()
        raise HTTPException(status_code=400, detail=f"Invalid test type. Must be one of: {', '.join(available)}")

    test_id = make_test_id(test_type, game_url, time.time())
    logger.info(f"[{test_id}] Starting test '{test_type}' for URL {game_url}")

    service = test_service_factory.get_service(test_type)
    if service is None:
        raise HTTPException(status_code=400, detail=f"No service registered for test type '{test_type}'")

    # For Regression, get its predefined flow (list of class_ids)
    flow: List[int] = []
    if test_type == "Regression" and hasattr(service, "CLASS_FLOW"):
        flow = getattr(service, "CLASS_FLOW")  # type: ignore
    # Extend here: other services can expose their own flow property similarly.

    if not flow:
        # Fallback: no stepwise flow defined, run the legacy full test
        test_execution_request = TestExecutionRequest(
            game_url=game_url,
            test_type=test_type,
            additional_params={},
            image_data=None
        )
        result = await test_service_factory.execute_test(test_type, test_execution_request)
        return RunTestResponse(
            test_id=result.test_id,
            next_step=NextStepInfo(
                class_id=-1,
                clickable=False,
                coordinates=None,
                instructions="Legacy full-run executed; no per-step flow"
            )
        )

    # Initialize execution context
    executions[test_id] = {
        "flow": flow,
        "current": 0,
        "history": [],
        "game_url": game_url,
        "test_type": test_type,
        "started_at": time.time(),
    }

    first_class_id = flow[0]
    return RunTestResponse(
        test_id=test_id,
        next_step=NextStepInfo(
            class_id=first_class_id,
            clickable=True,
            coordinates=None,
            instructions=f"Locate and interact with class_id {first_class_id}"
        )
    )

@app.post("/run-test-step", response_model=StepResponse)
async def run_test_step(req: StepRequest):
    exec_ctx = executions.get(req.test_id)
    if not exec_ctx:
        raise HTTPException(status_code=404, detail="Unknown test_id")

    flow: List[int] = exec_ctx["flow"]
    current_idx: int = exec_ctx["current"]

    if current_idx >= len(flow):
        raise HTTPException(status_code=400, detail="Flow already complete")

    expected_class_id = flow[current_idx]
    if req.class_id != expected_class_id:
        raise HTTPException(
            status_code=400,
            detail=f"Unexpected class_id. Expected {expected_class_id}, got {req.class_id}"
        )

    logger.info(f"[{req.test_id}] Processing step class_id={req.class_id} (index {current_idx})")

    # Prepare detection request
    try:
        _ = safe_decode_base64(req.screenshot)  # validation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    detect_service = test_service_factory.get_service("UI Element Detection")
    if not detect_service:
        raise HTTPException(status_code=500, detail="Detection service unavailable")

    detect_request = TestExecutionRequest(
        game_url=exec_ctx["game_url"],
        test_type="UI Element Detection",
        additional_params={"class_ids": [expected_class_id]},
        image_data=req.screenshot
    )

    detect_response = await detect_service.execute_test(detect_request) 

    click_targets = detect_response.results.get("click_targets", [])
    target = click_targets[0] if click_targets else {}
    confidence = target.get("confidence", 0.0) if isinstance(target, dict) else 0.0
    click_x = target.get("click_x") if isinstance(target, dict) else None
    click_y = target.get("click_y") if isinstance(target, dict) else None
    bbox = target.get("bounding_box") if isinstance(target, dict) else None

    passed =  (click_x is not None and click_y is not None)

    # Record history entry
    exec_ctx["history"].append({
        "class_id": expected_class_id,
        "passed": passed,
        "detection": {
            "click_x": click_x,
            "click_y": click_y,
            "confidence": confidence,
            "bounding_box": bbox
        },
        "action_result": req.action_result,
        "timestamp": time.time()
    })

    if passed:
        exec_ctx["current"] += 1

    # Build step_result
    detection_info = None
    if click_x is not None and click_y is not None:
        detection_info = DetectionInfo(
            class_id=expected_class_id,
            click_x=click_x,
            click_y=click_y,
            confidence=confidence,
            bounding_box=bbox
        )
    step_result = StepResult(
        class_id=expected_class_id,
        passed=passed,
        detection=detection_info
    )

    # Determine next step / completion
    if exec_ctx["current"] >= len(flow):
        all_passed = all(h["passed"] for h in exec_ctx["history"])
        final_status = "success" if all_passed else "partial"
        final_result = {
            "status": final_status,
            "history": exec_ctx["history"]
        }
        return StepResponse(
            status="complete",
            step_result=step_result,
            final_result=final_result
        )

    next_class_id = flow[exec_ctx["current"]]
    # Suggest current click coordinates back so Electron can perform click
    next_step = NextStepInfo(
        class_id=next_class_id,
        clickable=True,
        coordinates={"x": click_x, "y": click_y} if passed and click_x is not None and click_y is not None else None,
        instructions=f"Proceed to class_id {next_class_id}"
    )

    return StepResponse(
        status="continue",
        step_result=step_result,
        next_step=next_step
    )

@app.get("/test-results/{test_id}")
async def get_test_results(test_id: str):
    exec_ctx = executions.get(test_id)
    if not exec_ctx:
        raise HTTPException(status_code=404, detail="Test execution not found")

    flow = exec_ctx["flow"]
    history = exec_ctx["history"]
    completed = exec_ctx["current"] >= len(flow)
    overall = (
        "success" if completed and all(h["passed"] for h in history)
        else ("partial" if completed else "in_progress")
    )

    return {
        "test_id": test_id,
        "test_type": exec_ctx.get("test_type"),
        "game_url": exec_ctx.get("game_url"),
        "status": overall,
        "started_at": exec_ctx.get("started_at"),
        "current_index": exec_ctx.get("current"),
        "flow": flow,
        "history": history
    }

# Run server on port 7000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )