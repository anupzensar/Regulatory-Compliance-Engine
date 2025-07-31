from fastapi import APIRouter, Depends, status, Response, HTTPException
from . import pymodels
import logging
from config import settings

router = APIRouter()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)



@router.get("/", response_model=dict)
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


@router.post("/run-test", response_model=pymodels.TestResponse)
async def run_test(request: pymodels.TestRequest):
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
        
        return pymodels.TestResponse(
            status="success",
            message=f"Test '{request.testType}' submitted successfully for URL: {request.gameUrl}",
            test_id=f"test_{hash(str(request.gameUrl) + request.testType) % 10000}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing test request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
