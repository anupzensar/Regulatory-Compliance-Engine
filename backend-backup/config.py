import os
from typing import List

class Settings:
    """Application settings"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "7000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # CORS settings - Allow Electron app and development servers
    ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
    if ALLOWED_ORIGINS_ENV:
        ALLOWED_ORIGINS: List[str] = ALLOWED_ORIGINS_ENV.split(",")
    else:
        # For Electron integration, we'll be more permissive
        # In production, you should specify exact origins
        ALLOWED_ORIGINS: List[str] = ["*"]  # Allow all origins for Electron compatibility
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # API settings
    API_TITLE: str = os.getenv("API_TITLE", "Regulatory Compliance Engine API")
    API_DESCRIPTION: str = os.getenv(
        "API_DESCRIPTION", 
        "A platform for automated regulatory compliance testing of online games"
    )
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

settings = Settings()