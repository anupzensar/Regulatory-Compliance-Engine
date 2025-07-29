from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn
import logging
from config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["*"],
)

# Pydantic models for request validation
class TestRequest(BaseModel):
    gameUrl: HttpUrl
    testType: str

class TestResponse(BaseModel):
    status: str
    message: str
    test_id: str = None

@app.get("/", response_model=dict)
def read_root():
    """Health check endpoint"""
    return {"message": "Regulatory Compliance Engine API is running", "status": "healthy"}

# Valid test types
VALID_TEST_TYPES = {
    "Session Reminder",
    "Playcheck Regulation – limited to the base game",
    "Multiple Spin Test – limited to the base game",
    "Banking",
    "Practice Play",
    "Max Bet Limit Testing"
}

@app.post("/run-test", response_model=TestResponse)
async def run_test(request: TestRequest):
    """Submit a compliance test for execution"""
    try:
        # Validate test type
        if request.testType not in VALID_TEST_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid test type. Must be one of: {', '.join(VALID_TEST_TYPES)}"
            )
        
        logger.info(f"Received test request - URL: {request.gameUrl}, Type: {request.testType}")
        
        # TODO: Implement actual test execution logic here
        # For now, just log and return success
        
        return TestResponse(
            status="success",
            message=f"Test '{request.testType}' submitted successfully for URL: {request.gameUrl}",
            test_id=f"test_{hash(str(request.gameUrl) + request.testType) % 10000}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing test request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Run server on port 7000
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )