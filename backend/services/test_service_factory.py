from typing import Dict, Optional
import logging
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse
from .session_reminder_service import SessionReminderService
from .playcheck_service import PlaycheckService
from .multiple_spin_service import MultipleSpinService
from .banking_service import BankingService
from .practice_play_service import PracticePlayService
from .max_bet_limit_service import MaxBetLimitService
from .detect_service import DetectService
from .regression_service import RegressionService

logger = logging.getLogger(__name__)

class TestServiceFactory:
    """Factory class for managing test services"""
    
    def __init__(self):
        self._services: Dict[str, BaseTestService] = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all available test services"""
        services = [
            SessionReminderService(),
            PlaycheckService(),
            MultipleSpinService(),
            BankingService(),
            PracticePlayService(),
            MaxBetLimitService(),
            DetectService(),
            RegressionService()
        ]
        
        for service in services:
            self._services[service.get_test_type()] = service
            logger.info(f"Registered service: {service.get_test_type()}")
    
    def get_service(self, test_type: str) -> Optional[BaseTestService]:
        """Get a service by test type"""
        return self._services.get(test_type)
    
    def get_available_test_types(self) -> list:
        """Get list of all available test types"""
        return list(self._services.keys())
    
    def is_valid_test_type(self, test_type: str) -> bool:
        """Check if a test type is valid"""
        return test_type in self._services
    
    async def execute_test(self, test_type: str, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute a test using the appropriate service"""
        service = self.get_service(test_type)
        if not service:
            raise ValueError(f"No service found for test type: {test_type}")
        
        # Validate the request
        if not service.validate_request(request):
            raise ValueError(f"Invalid request for test type: {test_type}")
        
        # Execute the test
        return await service.execute_test(request)

test_service_factory = TestServiceFactory()
