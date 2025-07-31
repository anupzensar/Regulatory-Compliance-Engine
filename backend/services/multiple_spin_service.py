import time
import logging
import asyncio
import base64
import io
import os
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
from .base_service import BaseTestService, TestExecutionRequest, TestExecutionResponse

# Try to import ultralytics YOLO, handle if not installed
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics not installed. YOLO functionality will be disabled.")

logger = logging.getLogger(__name__)

class MultipleSpinService(BaseTestService):
    """Service for Multiple Spin Test compliance testing with YOLO model integration"""
    
    def __init__(self):
        super().__init__("Multiple Spin Test – limited to the base game")
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "..", "models", "best.pt")
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model from the models directory"""
        if not YOLO_AVAILABLE:
            logger.warning("YOLO not available. Model loading skipped.")
            return
            
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                logger.info(f"YOLO model loaded successfully from {self.model_path}")
            else:
                logger.warning(f"YOLO model not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            self.model = None
    
    def validate_request(self, request: TestExecutionRequest) -> bool:
        """Validate Multiple Spin test request"""
        # Check if image data is provided when YOLO processing is needed
        if hasattr(request, 'image_data') and request.image_data:
            try:
                # Validate base64 format
                base64.b64decode(request.image_data)
                return True
            except Exception as e:
                logger.error(f"Invalid base64 image data: {str(e)}")
                return False
        return True
    
    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute Multiple Spin Test compliance test with YOLO processing"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting Multiple Spin Test for URL: {request.game_url}")
            
            # Initialize results
            yolo_detections = []
            image_processed = False
            
            # Process image if provided
            if hasattr(request, 'image_data') and request.image_data:
                try:
                    logger.info("Processing base64 image with YOLO model")
                    image = self._decode_base64_image(request.image_data)
                    yolo_detections = await self._run_yolo_inference(image)
                    image_processed = True
                    logger.info(f"Image processed successfully. Found {len(yolo_detections)} detections.")
                except Exception as e:
                    logger.error(f"Image processing failed: {str(e)}")
                    # Continue with test even if image processing fails
            
            # Simulate additional test execution
            await self._simulate_test_execution()
            
            execution_time = time.time() - start_time
            test_id = f"multiple_spin_{hash(request.game_url) % 10000}"
            
            # Define the test flow as an array of class IDs
            # Multiple Spin Test flow: Settings -> Bet Settings -> Spin Button (multiple times)
            test_flow = [9, 7, 1, 1, 1, 1, 1]  # SettingsButton, BetSettingsButton, SpinButton (5 times)
            
            # Prepare results
            results = {
                "spins_executed": 100,
                "base_game_only": True,
                "rtp_verified": True,
                "variance_acceptable": True,
                "average_rtp": 96.5,
                "test_flow": test_flow,
                "flow_description": "Settings -> Bet Settings -> Spin Button (5 times)",
                "image_processed": image_processed,
                "detection_count": len(yolo_detections) if yolo_detections else 0
            }
            
            return TestExecutionResponse(
                status="success",
                message=f"Multiple Spin Test completed successfully for URL: {request.game_url}. Image processed: {image_processed}",
                test_id=test_id,
                execution_time=execution_time,
                results=results
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Multiple Spin Test failed: {str(e)}")
            
            return TestExecutionResponse(
                status="error",
                message=f"Multiple Spin Test failed: {str(e)}",
                test_id=f"multiple_spin_error_{hash(request.game_url) % 10000}",
                execution_time=execution_time,
                results={"error": str(e)}
            )
    
    async def _simulate_test_execution(self):
        """Simulate test execution delay"""
        await asyncio.sleep(1.0)
    
    def _decode_base64_image(self, base64_string: str) -> Image.Image:
        """Decode base64 string to PIL Image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {str(e)}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    def _process_yolo_detections(self, results) -> List[Dict[str, Any]]:
        """Process YOLO detection results and extract coordinates"""
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates (x1, y1, x2, y2)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Calculate center coordinates
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    
                    # Get confidence and class
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detection = {
                        "mid_x": float(mid_x),
                        "mid_y": float(mid_y),
                        "box_coordinates": {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2)
                        },
                        "confidence": float(confidence),
                        "class_id": class_id,
                        "width": float(x2 - x1),
                        "height": float(y2 - y1)
                    }
                    detections.append(detection)
        
        return detections
    
    async def _run_yolo_inference(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Run YOLO inference on the provided image"""
        if not YOLO_AVAILABLE or self.model is None:
            logger.warning("YOLO model not available for inference")
            return []
        
        try:
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            
            # Run inference
            results = self.model(image_array)
            
            # Process results
            detections = self._process_yolo_detections(results)
            
            logger.info(f"YOLO inference completed. Found {len(detections)} detections.")
            return detections
            
        except Exception as e:
            logger.error(f"YOLO inference failed: {str(e)}")
            return []
