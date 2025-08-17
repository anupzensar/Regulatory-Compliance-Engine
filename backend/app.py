# filepath: app.py
import base64
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
import uvicorn
import logging

from config import settings
from services.test_service_factory import test_service_factory
from services.base_service import TestExecutionRequest

from PIL import Image
import io
import easyocr
import numpy as np

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

# Pydantic models for request/response
class TestRequest(BaseModel):
    gameUrl: HttpUrl
    testType: str
    selectedPolicy: Optional[str] = None
    selectedTestSuite: Optional[str] = None
    selectedTestCases: Optional[list[str]] = None
    class_id: Optional[int] = None
    imageData: Optional[str] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict, alias='additionalParams')

class TestResponse(BaseModel):
    status: str
    message: str
    test_id: Optional[str] = None
    results: Dict[str, Any] = {}
    # expose an optional script at top-level so the frontend can run it
    script: Optional[str] = None

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

        # Bubble up an optional 'script' from the service results to top-level
        script = None
        if isinstance(test_result.results, dict):
            script = test_result.results.get("script")

        return TestResponse(
            status=test_result.status,
            message=test_result.message,
            test_id=test_result.test_id,
            results=test_result.results,
            script=script
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

# OCR input model

from pydantic import BaseModel

class OCRRequest(BaseModel):
    imageData: str
    text: str

@app.post("/ocr/find-text")
async def find_text_in_image(payload: OCRRequest):
    reader = easyocr.Reader(['en'], gpu=False)
    image_data = base64.b64decode(payload.imageData)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    np_image = np.array(image)

    results = reader.readtext(np_image)

    query = payload.text.strip().lower()

    for (bbox, text, confidence) in results:
        if query in text.strip().lower():
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            x_center = int(sum(x_coords) / len(x_coords))
            y_center = int(sum(y_coords) / len(y_coords))

            return {
                "found": True,
                "text": text,
                "x": x_center,
                "y": y_center,
                "confidence": round(confidence * 100, 2)
            }

    return {"found": False}

# Run server on configured host/port
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )
