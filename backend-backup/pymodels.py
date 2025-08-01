from pydantic import BaseModel
from typing import Optional , List

# Pydantic models for request validation
class TestRequest(BaseModel):
    gameUrl: HttpUrl
    testType: str

class TestResponse(BaseModel):
    status: str
    message: str
    test_id: str = None