import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.test_service_factory import test_service_factory
from services.base_service import TestExecutionRequest

async def test_microservices():
    """Test all microservices"""
    print("Testing Microservice Architecture")
    print("=" * 50)
    
    # Get available test types
    test_types = test_service_factory.get_available_test_types()
    print(f"Available test types: {len(test_types)}")
    for test_type in test_types:
        print(f"  - {test_type}")
    
    print("\n" + "=" * 50)
    print("Testing each service:")
    
    # Test each service
    test_url = "https://example-game.com"
    
    for test_type in test_types:
        print(f"\nTesting: {test_type}")
        print("-" * 30)
        
        try:
            # Create test request
            request = TestExecutionRequest(
                game_url=test_url,
                test_type=test_type,
                additional_params={}
            )
            
            # Execute test
            result = await test_service_factory.execute_test(test_type, request)
            
            print(f"Status: {result.status}")
            print(f"Message: {result.message}")
            print(f"Test ID: {result.test_id}")
            print(f"Execution Time: {result.execution_time:.2f}s")
            print(f"Results: {result.results}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_microservices())
