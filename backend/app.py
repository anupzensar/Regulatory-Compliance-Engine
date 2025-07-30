from fastapi import FastAPI, HTTPException , APIRouter
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
from config import settings

# include routers
from routers import temp
from routers import regression



app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)


# app.include_router(regression)
app.include_router(temp)
# CORS middleware with configurable origins - supports Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ALLOWED_ORIGINS == ["*"] else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["*"],
)


# Run server on port 7000
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )