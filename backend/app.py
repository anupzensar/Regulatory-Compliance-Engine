import sys
import asyncio
from typing import Any, Dict

# Now import everything else
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
import uvicorn
import logging
from config import settings
from services.test_service_factory import test_service_factory
from services.base_service import TestExecutionRequest
from fastapi import Body

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

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

# Pydantic models for request validation
# TODO: Create a paramenter object where we can add anything according to time
class TestRequest(BaseModel):
    gameUrl: HttpUrl
    testType: str
    selectedPolicy: str | None = None
    selectedTestSuite: str | None = None
    selectedTestCases: list[str] | None = None
    class_id: int | None = None
    imageData: str | None = None
    additional_params: Dict[str, Any] = Field(default_factory=dict, alias='additionalParams')
    
    
class TestResponse(BaseModel):
    status: str
    message: str
    test_id: str = None
    results: Dict[str, Any] = {}
    
class RegressionRequest(BaseModel):
    url: HttpUrl
    # headless: bool = True

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



@app.post("/regression-test")
async def run_regression_test(request: RegressionRequest):
    print(f"Running regression test for URL: {request.url}")
    print(f'sending request to regression service')
    return {
        "script": """
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
    }



@app.post("/run-test", response_model=TestResponse)
async def run_test(request: TestRequest):
    """Submit a compliance test for execution using microservice architecture"""
    try:
        if not test_service_factory.is_valid_test_type(request.testType):
            available_types = test_service_factory.get_available_test_types()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid test type. Must be one of: {', '.join(available_types)}"
            )

        logger.info(f"Received test request - URL: {request.gameUrl}, Type: {request.testType}")

        # Merge additional params (support both camelCase and snake_case inputs)
        merged_params: Dict[str, Any] = dict(request.additional_params or {})
        if request.selectedPolicy is not None:
            merged_params["selectedPolicy"] = request.selectedPolicy
        if request.selectedTestSuite is not None:
            merged_params["selectedTestSuite"] = request.selectedTestSuite
        if request.selectedTestCases is not None:
            merged_params["selectedTestCases"] = request.selectedTestCases
        # Normalize class_ids
        if "class_ids" not in merged_params and request.class_id is not None:
            merged_params["class_ids"] = [request.class_id]

        # Image data may come at top-level or inside additional_params
        image_data = request.imageData or merged_params.get("imageData")

        test_execution_request = TestExecutionRequest(
            game_url=str(request.gameUrl),
            test_type=request.testType,
            additional_params=merged_params,
            image_data=image_data,
        )

        test_result = await test_service_factory.execute_test(
            request.testType,
            test_execution_request,
        )

        return TestResponse(
            status=test_result.status,
            message=test_result.message,
            test_id=test_result.test_id,
            results=test_result.results,
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing test request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
@app.get("/test-results/{test_id}", response_model=dict)
async def get_test_results(test_id: str):
    """Get detailed test results (placeholder for future implementation)"""
    # TODO: Implement test result storage and retrieval
    return {
        "test_id": test_id,
        "status": "completed",
        "message": "Test results retrieval not yet implemented",
        "note": "This endpoint will be implemented when test result storage is added"
    }



# Run server on port 7000
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )