# # filepath: services/regression_service.py
# import time
# import logging
# import asyncio
# import hashlib
# from typing import Dict, Any, List
# from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

# logger = logging.getLogger(__name__)

# # Regression flow as class IDs
# REGRESSION_FLOW: List[int] = [0, 1, 1, 15, 7, 10, 11]
# # Confidence threshold for considering a detection as passed
# DEFAULT_CONFIDENCE_THRESHOLD = 0.5


# def make_stable_test_id(test_type: str, game_url: str, timestamp: float) -> str:
#     base = f"{test_type}|{game_url}|{timestamp}"
#     digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
#     return f"{test_type.lower().replace(' ', '_')}_{digest[:12]}"


# class HelpFileService(BaseTestService):
#     """Service for HelpFile compliance testing"""

    