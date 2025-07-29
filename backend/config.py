import os
from typing import List

class Settings:
    """Application settings"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "7000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
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
