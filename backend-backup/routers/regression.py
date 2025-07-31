from fastapi import FastAPI, HTTPException , APIRouter

router = APIRouter(
    
    prefix="/regression",
    tags=["regression"]
)


@router.get("/")
def read_root():
    """Health check endpoint for regression tests"""
    return {"message": "Regression API is running", "status": "healthy"}
    
