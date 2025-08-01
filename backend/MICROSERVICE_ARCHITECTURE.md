# Microservice Architecture for Regulatory Compliance Engine

## Overview


The backend uses a microservice architecture pattern for handling different test types. Each compliance test type is handled by its own dedicated service, making the system modular, maintainable, and extensible.
The backend has been refactored to use a microservice architecture pattern for handling different test types. Each compliance test type is now handled by its own dedicated service, making the system more modular, maintainable, and extensible.
## Architecture

### Base Components

- **BaseTestService**: Abstract base class that defines the interface for all test services
- **TestExecutionRequest**: Standard request model for all test executions (uses snake_case fields)
- **TestExecutionRequest**: Standard request model for all test executions
- **TestExecutionResponse**: Standard response model with detailed execution results
- **TestServiceFactory**: Factory class that manages all test services and routes requests

### Available Services

1. **SessionReminderService** - Handles "Session Reminder" compliance tests
2. **PlaycheckService** - Handles "Playcheck Regulation – limited to the base game" tests
3. **MultipleSpinService** - Handles "Multiple Spin Test – limited to the base game" tests
4. **BankingService** - Handles "Banking" compliance tests
5. **PracticePlayService** - Handles "Practice Play" compliance tests
6. **MaxBetLimitService** - Handles "Max Bet Limit Testing" compliance tests
7. **DetectService** - Handles "UI Element Detection" for image-based coordinate detection (NEW)
## Directory Structure

```
backend/
├── app.py                          # Main FastAPI application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── test_microservices.py           # Test script for services
└── services/                       # Microservices directory
    ├── __init__.py
    ├── base_service.py             # Base service interface and models
├── requirements.txt                 # Python dependencies
├── test_microservices.py           # Test script for services
└── services/                       # Microservices directory
    ├── __init__.py
    ├── base_service.py             # Base service interface
    ├── test_service_factory.py     # Service factory and router
    ├── session_reminder_service.py
    ├── playcheck_service.py
    ├── multiple_spin_service.py
    ├── banking_service.py
    ├── practice_play_service.py
    ├── max_bet_limit_service.py
    └── detect_service.py           # NEW: UI Element Detection service
    └── max_bet_limit_service.py
```

## API Endpoints

### GET /

Health check endpoint

### GET /test-types

Health check endpoint

### GET /test-types
Returns all available test types and count
```json
{
  "test_types": ["Session Reminder", "Banking", ...],
  "count": 7
  "count": 6
}
```

### POST /run-test

Execute a compliance test
```json
// Request
{
  "gameUrl": "https://example-game.com",
  "testType": "Session Reminder"
}

// Response
{
  "status": "success",
  "message": "Session Reminder test completed successfully for URL: https://example-game.com/",
  "test_id": "session_reminder_147"
}
```

### GET /test-results/{test_id}
Get detailed test results (placeholder for future implementation)

## Service Interface

Each service implements the `BaseTestService` interface:

```python
class BaseTestService(ABC):
    @abstractmethod
    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        pass
    
    @abstractmethod
    def validate_request(self, request: TestExecutionRequest) -> bool:
        pass
```

## Service Features

Each service provides:
- **Asynchronous execution** for non-blocking operations
- **Request validation** specific to the test type
- **Detailed response** with execution time and test results
- **Error handling** with proper logging
- **Simulation mode** for development and testing

## Example Service Response

```python
TestExecutionResponse(
    status="success",
    message="Banking test completed successfully for URL: https://example-game.com",
    test_id="banking_147",
    execution_time=0.80,
    results={
        "deposit_functionality": True,
        "withdrawal_functionality": True,
        "balance_tracking": True,
        "transaction_logging": True,
        "security_compliance": True
    }
)
```

## Running the Application

1. Start the server:
```bash
python app.py
# or
python -m uvicorn app:app --host 127.0.0.1 --port 7000 --reload
```

2. Test the microservices:
```bash
python test_microservices.py
```

## Adding New Test Types

To add a new test type:

1. Create a new service class inheriting from `BaseTestService`
2. Implement the required methods (`execute_test`, `validate_request`)
3. Add the service to the `TestServiceFactory._initialize_services()` method
4. The new test type will automatically be available via the API

## Benefits

- **Modularity**: Each test type is isolated in its own service
- **Scalability**: Services can be easily extended or replaced
- **Maintainability**: Clear separation of concerns
- **Testability**: Each service can be tested independently
- **Extensibility**: Easy to add new test types without modifying existing code

## Future Enhancements

- Implement actual test execution logic for each service
- Add result persistence and retrieval
- Implement service health monitoring
- Add configuration management for each service
- Implement parallel test execution
- Add detailed logging and metrics collection
