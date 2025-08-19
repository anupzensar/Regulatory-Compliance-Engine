from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel, Field

class TestExecutionRequest(BaseModel):
    """Base request model for test execution"""
    game_url: str
    test_type: str
    additional_params: Dict[str, Any] = Field(default_factory=dict)
    image_data: str | None = None

class TestExecutionResponse(BaseModel):
    """Base response model for test execution"""
    status: str
    message: str
    test_id: str
    execution_time: float = 0.0
    test_flow: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)

class BaseTestService(ABC):
    """Abstract base class for all test services"""
    
    def __init__(self, test_type: str):
        self.test_type = test_type
    
    @abstractmethod
    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute the specific test type"""
        pass
    
    @abstractmethod
    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Validate the request for this specific test type"""
        pass
    
    def get_test_type(self) -> str:
        """Get the test type this service handles"""
        return self.test_type
