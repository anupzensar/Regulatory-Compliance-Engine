# filepath: app.py
import base64
import difflib
import io
import logging
import re
from typing import Any, Dict, List, Optional
import os
from datetime import datetime

import easyocr
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, Field, HttpUrl

from config import settings
from services.base_service import TestExecutionRequest
from services.test_service_factory import test_service_factory

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ALLOWED_ORIGINS == ["*"] else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ✅ PERFORMANCE FIX: Initialize the OCR reader once when the application starts.
# This avoids the slow model loading process on every API request.
logger.info("Initializing EasyOCR reader...")
ocr_reader = easyocr.Reader(['en'], gpu=False)
logger.info("EasyOCR reader initialized.")

# --- Pydantic Models for Request/Response ---

class TestRequest(BaseModel):
    gameUrl: HttpUrl
    testType: str
    selectedPolicy: Optional[str] = None
    selectedTestSuite: Optional[str] = None
    selectedTestCases: Optional[List[str]] = None
    class_id: Optional[int] = None
    imageData: Optional[str] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict, alias='additionalParams')

class TestResponse(BaseModel):
    status: str
    message: str
    test_id: Optional[str] = None
    results: Dict[str, Any] = Field(default_factory=dict)
    script: Optional[str] = None

class OCRRequest(BaseModel):
    imageData: str
    text: str

# --- Helper Functions for OCR ---

def normalize_text(s: str) -> str:
    """Lowercase the text and collapse all whitespace to single spaces."""
    return re.sub(r"\s+", " ", s.strip().lower())

def is_close_match(query: str, candidate: str, cutoff: float = 0.8) -> bool:
    """Perform a fuzzy match using SequenceMatcher to find similar text."""
    return difflib.SequenceMatcher(None, query, candidate).ratio() >= cutoff

# --- API Endpoints ---

@app.get("/", response_model=dict)
def read_root():
    """Health check endpoint."""
    return {"message": "Regulatory Compliance Engine API is running", "status": "healthy"}

@app.get("/test-types", response_model=dict)
def get_test_types():
    """Get all available test types from the service factory."""
    available_types = test_service_factory.get_available_test_types()
    return {
        "test_types": available_types,
        "count": len(available_types)
    }

@app.post("/run-test", response_model=TestResponse)
async def run_test(request: TestRequest):
    """Submit a compliance test for execution."""
    try:
        if not test_service_factory.is_valid_test_type(request.testType):
            available_types = test_service_factory.get_available_test_types()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid test type. Must be one of: {', '.join(available_types)}"
            )

        logger.info(f"Received test request - URL: {request.gameUrl}, Type: {request.testType}")

        # Merge parameters to flexibly handle inputs from different frontend components,
        # supporting both top-level fields and nested 'additionalParams'.
        merged_params: Dict[str, Any] = dict(request.additional_params or {})
        if request.selectedPolicy is not None:
            merged_params["selectedPolicy"] = request.selectedPolicy
        if request.selectedTestSuite is not None:
            merged_params["selectedTestSuite"] = request.selectedTestSuite
        if request.selectedTestCases is not None:
            merged_params["selectedTestCases"] = request.selectedTestCases

        # Normalize class_ids to ensure it's always a list
        if "class_ids" not in merged_params and request.class_id is not None:
            merged_params["class_ids"] = [request.class_id]

        # Image data may come at top-level or inside additional_params
        image_data = request.imageData or merged_params.get("imageData")

        test_execution_request = TestExecutionRequest(
            game_url=str(request.gameUrl),
            test_type=request.testType,
            additional_params=merged_params,
            image_data=image_data,
        )

        test_result = await test_service_factory.execute_test(
            request.testType,
            test_execution_request,
        )

        # Bubble up an optional 'script' from the service results to the top-level response
        script = None
        if isinstance(test_result.results, dict):
            script = test_result.results.get("script")

        return TestResponse(
            status=test_result.status,
            message=test_result.message,
            test_id=test_result.test_id,
            results=test_result.results,
            script=script
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing test request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/test-results/{test_id}", response_model=dict)
async def get_test_results(test_id: str):
    """Get detailed test results (placeholder for future implementation)."""
    # TODO: Implement test result storage and retrieval
    return {
        "test_id": test_id,
        "status": "completed",
        "message": "Test results retrieval not yet implemented",
        "note": "This endpoint will be implemented when test result storage is added"
    }

@app.post("/ocr/find-text")
async def find_text_in_image(payload: OCRRequest):
    """Finds specified text in an image and returns its coordinates."""
    try:
        image_data = base64.b64decode(payload.imageData)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        np_image = np.array(image)

        # Use the globally pre-loaded OCR reader for fast inference
        results = ocr_reader.readtext(np_image)

        query = normalize_text(payload.text)
        matches = []
        for (bbox, text, confidence) in results:
            candidate = normalize_text(text)
            if query in candidate or is_close_match(query, candidate):
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                x_center = int(sum(x_coords) / len(x_coords))
                y_center = int(sum(y_coords) / len(y_coords))

                matches.append({
                    "text": text,
                    "x": x_center,
                    "y": y_center,
                    "confidence": round(confidence * 100, 2)
                })

        if not matches:
            return {"found": False, "matches": []}

        # Return the best match (highest confidence) along with all other potential matches
        best_match = max(matches, key=lambda m: m["confidence"])
        return {
            "found": True,
            "best": best_match,
            "matches": matches
        }
    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process image for OCR.")

# --- Validation handler to convert 422 to 400 ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Request validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid request", "errors": exc.errors()},
    )

# --- Reports: static mount and generation endpoint ---

# Ensure reports directory exists (mount is registered after the endpoint)
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class ReportStep(BaseModel):
    step_index: int
    class_id: int | None = None
    x: float | None = None
    y: float | None = None
    imageData: str | None = None  # data URI or base64
    timestamp: str | None = None

class ReportRequest(BaseModel):
    test_id: str | None = None
    gameUrl: str | None = None
    testType: str | None = None
    logs: List[str] = []
    steps: List[ReportStep] = []

@app.post("/reports/generate")
async def generate_report(payload: ReportRequest):
    """Generate a PDF report containing logs, coordinates, and step images.
    Saves PDF to backend/reports and returns a URL to download.
    """
    # Try to import reportlab lazily
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.utils import ImageReader
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="PDF generator not available. Please install 'reportlab' in the backend environment.",
        )

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base_name = f"report_{payload.test_id or 'na'}_{ts}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, base_name)

    try:
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Cover page
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2.5*cm, "Regulatory Compliance Test Report")
        c.setFont("Helvetica", 11)
        c.drawString(2*cm, height - 3.5*cm, f"Test ID: {payload.test_id or '-'}")
        c.drawString(2*cm, height - 4.0*cm, f"Test Type: {payload.testType or '-'}")
        c.drawString(2*cm, height - 4.5*cm, f"Game URL: {payload.gameUrl or '-'}")
        c.drawString(2*cm, height - 5.0*cm, f"Generated (UTC): {ts}")
        c.showPage()

        # Logs page(s)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 2.5*cm, "Console Logs")
        c.setFont("Helvetica", 10)
        y = height - 3.2*cm
        for line in payload.logs or []:
            # Manual line wrapping
            max_chars = 110
            chunks = [line[i:i+max_chars] for i in range(0, len(line), max_chars)] or [""]
            for chunk in chunks:
                if y < 2*cm:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 2*cm
                c.drawString(2*cm, y, chunk)
                y -= 0.5*cm
        c.showPage()

        # Steps with coordinates and optional images
        for step in payload.steps or []:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, height - 2.5*cm, f"Step {step.step_index}")
            c.setFont("Helvetica", 11)
            c.drawString(2*cm, height - 3.2*cm, f"Class ID: {step.class_id if step.class_id is not None else '-'}")
            c.drawString(2*cm, height - 3.8*cm, f"Click Coordinates: ({step.x if step.x is not None else '-'}, {step.y if step.y is not None else '-'})")
            if step.timestamp:
                c.drawString(2*cm, height - 4.4*cm, f"Timestamp: {step.timestamp}")

            # Draw image if provided
            y_cursor = height - 5.2*cm
            if step.imageData:
                try:
                    data = step.imageData
                    # Accept data URI or raw base64
                    if "," in data:
                        data = data.split(",", 1)[1]
                    img_bytes = base64.b64decode(data)
                    img = ImageReader(io.BytesIO(img_bytes))
                    # Fit into area
                    img_max_w = width - 4*cm
                    img_max_h = height - 10*cm
                    # Assume original size unknown; draw with max box keeping aspect ratio
                    iw, ih = img.getSize()
                    scale = min(img_max_w/iw, img_max_h/ih)
                    dw, dh = iw*scale, ih*scale
                    c.drawImage(img, 2*cm, y_cursor - dh, width=dw, height=dh, preserveAspectRatio=True, mask='auto')
                    y_cursor = y_cursor - dh - 1*cm
                except Exception as img_err:
                    c.setFont("Helvetica", 10)
                    c.drawString(2*cm, y_cursor, f"[Image render failed: {img_err}]")
                    y_cursor -= 1*cm

            c.showPage()

        c.save()
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")

    url = f"/reports/{base_name}"
    return {"status": "success", "report_id": base_name, "url": url}

# Register static serving for reports AFTER defining the dynamic route so
# /reports/generate is handled by the API, and other /reports/* paths serve files.
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")