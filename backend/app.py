import sys
import asyncio

# Now import everything else
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
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
class TestRequest(BaseModel):
    gameUrl: HttpUrl
    testType: str
    imageData: str = None  # Optional base64 encoded image data

class TestResponse(BaseModel):
    status: str
    message: str
    test_id: str = None

class RegressionRequest(BaseModel):
    url: HttpUrl
    headless: bool = True

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
        # Validate test type using the service factory
        if not test_service_factory.is_valid_test_type(request.testType):
            available_types = test_service_factory.get_available_test_types()
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid test type. Must be one of: {', '.join(available_types)}"
            )
        
        logger.info(f"Received test request - URL: {request.gameUrl}, Type: {request.testType}")
        
        # Create test execution request
        test_execution_request = TestExecutionRequest(
            game_url=str(request.gameUrl),
            test_type=request.testType,
            additional_params={},
            image_data=request.imageData
        )
        
        # Execute test using the appropriate microservice
        test_result = await test_service_factory.execute_test(
            request.testType, 
            test_execution_request
        )
        
        # Convert microservice response to API response
        return TestResponse(
            status=test_result.status,
            message=test_result.message,
            test_id=test_result.test_id
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