import logging
import base64
import io
import os
from typing import Dict, Any, List, Optional, Tuple
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

class DetectService(BaseTestService):
    """Service for detecting UI elements and returning click coordinates"""
    
    def __init__(self):
        super().__init__("UI Element Detection")
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "..", "models", "best.pt")
        self.classes = self._load_classes()
        self._load_model()
    
    def _load_classes(self) -> List[str]:
        """Load class names from classes.json"""
        try:
            classes_path = os.path.join(os.path.dirname(__file__), "..", "models", "classes.json")
            if os.path.exists(classes_path):
                import json
                with open(classes_path, 'r') as f:
                    classes = json.load(f)
                logger.info(f"Loaded {len(classes)} classes from classes.json")
                return classes
            else:
                logger.warning("classes.json not found, using default class names")
                return [f"class_{i}" for i in range(17)]  # Fallback
        except Exception as e:
            logger.error(f"Failed to load classes: {str(e)}")
            return [f"class_{i}" for i in range(17)]  # Fallback
    
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
        """Validate detect request"""
        if not hasattr(request, 'image_data') or not request.image_data:
            logger.error("Image data is required for detection")
            return False
        
        if not hasattr(request, 'class_ids') or not request.additional_params.get('class_ids'):
            logger.error("Class IDs are required for detection")
            return False
            
        try:
            # Validate base64 format
            base64.b64decode(request.image_data)
            return True
        except Exception as e:
            logger.error(f"Invalid base64 image data: {str(e)}")
            return False
    
    async def execute_test(self, request: TestExecutionRequest) -> TestExecutionResponse:
        """Execute UI element detection and return click coordinates"""
        try:
            logger.info("Starting UI element detection")
            
            # Get class IDs to detect from request
            class_ids = request.additional_params.get('class_ids', [])
            if not class_ids:
                raise ValueError("No class IDs provided for detection")
            
            # Decode and process image
            image = self._decode_base64_image(request.image_data)
            detections = await self._run_yolo_inference(image)
            
            # Filter detections by requested class IDs and get click coordinates
            click_targets = self._get_click_targets(detections, class_ids)
            
            return TestExecutionResponse(
                status="success",
                message=f"Detection completed. Found {len(click_targets)} targets for {len(class_ids)} requested classes.",
                test_id=f"detect_{hash(str(class_ids)) % 10000}",
                execution_time=0.0,
                results={
                    "requested_classes": class_ids,
                    "click_targets": click_targets,
                    "total_detections": len(detections),
                    "matched_targets": len(click_targets)
                }
            )
            
        except Exception as e:
            logger.error(f"Detection failed: {str(e)}")
            return TestExecutionResponse(
                status="error",
                message=f"Detection failed: {str(e)}",
                test_id="detect_error",
                execution_time=0.0,
                results={"error": str(e)}
            )
    
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
                        "class_name": self.classes[class_id] if class_id < len(self.classes) else f"class_{class_id}",
                        "width": float(x2 - x1),
                        "height": float(y2 - y1)
                    }
                    detections.append(detection)
        
        return detections
    
    def _get_click_targets(self, detections: List[Dict[str, Any]], class_ids: List[int]) -> List[Dict[str, Any]]:
        """Get click targets for requested class IDs"""
        click_targets = []
        
        for class_id in class_ids:
            # Find the best detection for this class (highest confidence)
            best_detection = None
            best_confidence = 0.0
            
            for detection in detections:
                if (detection["class_id"] == class_id and 
                    detection["confidence"] > best_confidence):
                    best_detection = detection
                    best_confidence = detection["confidence"]
            
            if best_detection:
                click_target = {
                    "class_id": class_id,
                    "class_name": best_detection["class_name"],
                    "click_x": best_detection["mid_x"],
                    "click_y": best_detection["mid_y"],
                    "bounding_box": best_detection["box_coordinates"],
                    "confidence": best_detection["confidence"],
                    "width": best_detection["width"],
                    "height": best_detection["height"]
                }
                click_targets.append(click_target)
            else:
                logger.warning(f"No detection found for class_id {class_id}")
                # Add a placeholder for missing detection
                click_targets.append({
                    "class_id": class_id,
                    "class_name": self.classes[class_id] if class_id < len(self.classes) else f"class_{class_id}",
                    "click_x": None,
                    "click_y": None,
                    "bounding_box": None,
                    "confidence": 0.0,
                    "width": 0,
                    "height": 0,
                    "status": "not_detected"
                })
        
        return click_targets
