# filepath: app.py
import base64
import difflib
import io
import logging
import re
from typing import Any, Dict, List, Optional
import os
from datetime import datetime
import cv2

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ALLOWED_ORIGINS == ["*"] else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize the OCR reader once at startup
logger.info("Initializing EasyOCR reader...")
ocr_reader = easyocr.Reader(['en'], gpu=False)
logger.info("EasyOCR reader initialized.")

# --- Pydantic Models ---

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

# --- Helper Functions ---

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def is_close_match(query: str, candidate: str, cutoff: float = 0.8) -> bool:
    return difflib.SequenceMatcher(None, query, candidate).ratio() >= cutoff

# --- API Endpoints ---

@app.get("/", response_model=dict)
def read_root():
    return {"message": "Regulatory Compliance Engine API is running", "status": "healthy"}

@app.get("/test-types", response_model=dict)
def get_test_types():
    available_types = test_service_factory.get_available_test_types()
    return {"test_types": available_types, "count": len(available_types)}

@app.post("/run-test", response_model=TestResponse)
async def run_test(request: TestRequest):
    try:
        if not test_service_factory.is_valid_test_type(request.testType):
            available_types = test_service_factory.get_available_test_types()
            raise HTTPException(status_code=400, detail=f"Invalid test type: {', '.join(available_types)}")

        logger.info(f"Received test request - URL: {request.gameUrl}, Type: {request.testType}")

        merged_params: Dict[str, Any] = dict(request.additional_params or {})
        if request.selectedPolicy is not None: merged_params["selectedPolicy"] = request.selectedPolicy
        if request.selectedTestSuite is not None: merged_params["selectedTestSuite"] = request.selectedTestSuite
        if request.selectedTestCases is not None: merged_params["selectedTestCases"] = request.selectedTestCases
        if "class_ids" not in merged_params and request.class_id is not None: merged_params["class_ids"] = [request.class_id]
        
        image_data = request.imageData or merged_params.get("imageData")

        test_execution_request = TestExecutionRequest(
            game_url=str(request.gameUrl), test_type=request.testType,
            additional_params=merged_params, image_data=image_data,
        )

        test_result = await test_service_factory.execute_test(request.testType, test_execution_request)
        script = test_result.results.get("script") if isinstance(test_result.results, dict) else None

        return TestResponse(
            status=test_result.status, message=test_result.message,
            test_id=test_result.test_id, results=test_result.results, script=script
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
    return {"test_id": test_id, "status": "completed", "message": "Test results retrieval not yet implemented"}

@app.post("/ocr/find-text")
async def find_text_in_image(payload: OCRRequest):
    try:
        image_data = base64.b64decode(payload.imageData)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        np_image = np.array(image)

        results = ocr_reader.readtext(np_image)

        query = normalize_text(payload.text)
        matches = []

        def split_bbox_by_words(bbox, full_text):
            """
            Splits a bounding box into smaller boxes for each word.
            Assumes horizontal word layout.
            """
            words = full_text.split()
            if len(words) <= 1:
                return [(full_text, bbox)]

            min_x, max_x = min(p[0] for p in bbox), max(p[0] for p in bbox)
            min_y, max_y = min(p[1] for p in bbox), max(p[1] for p in bbox)

            total_width = max_x - min_x
            avg_char_width = total_width / max(1, len(full_text))

            word_boxes = []
            current_x = min_x

            for word in words:
                word_width = len(word) * avg_char_width
                word_bbox = [
                    (current_x, min_y),
                    (current_x + word_width, min_y),
                    (current_x + word_width, max_y),
                    (current_x, max_y),
                ]
                word_boxes.append((word, word_bbox))
                current_x += word_width + avg_char_width  # add spacing
            return word_boxes

        for (bbox, text, confidence) in results:
            # Split detected text into possible word boxes
            for word, word_bbox in split_bbox_by_words(bbox, text):
                candidate = normalize_text(word)

                if query == candidate or is_close_match(query, candidate):
                    x_coords = [p[0] for p in word_bbox]
                    y_coords = [p[1] for p in word_bbox]
                    center_x = int(sum(x_coords) / len(x_coords))
                    center_y = int(sum(y_coords) / len(y_coords))

                    matches.append({
                        "text": word,
                        "x": center_x,
                        "y": center_y,
                        "confidence": round(confidence * 100, 2)
                    })

        if not matches:
            return {"found": False, "matches": []}

        best_match = max(matches, key=lambda m: m["confidence"])
        return {
            "found": True,
            "best": best_match,
            "matches": matches
        }

    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process image for OCR.")

@app.post("/ocr/extract-paragraph")
async def extract_paragraph_from_image(payload: OCRRequest):
    try:
        image_data = base64.b64decode(payload.imageData)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        np_image = np.array(image)

        results = ocr_reader.readtext(np_image)

        if not results:
            return {"found": False, "paragraph": ""}

        # Sort by y (top to bottom), then x (left to right)
        sorted_results = sorted(results, key=lambda r: (min(p[1] for p in r[0]), min(p[0] for p in r[0])))

        extracted_texts = [text for (_, text, confidence) in sorted_results]

        # Join all texts into a paragraph
        paragraph = " ".join(extracted_texts)

        return {
            "found": True,
            "paragraph": paragraph.strip()
        }

    except Exception as e:
        logger.error(f"Error during OCR extraction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to extract text from image.")


@app.post("/ocr/extract-paragraph2")
async def extract_paragraph_from_image2(payload: OCRRequest):
    try:
        # Decode base64 to image
        image_data = base64.b64decode(payload.imageData)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        # ---------- Preprocessing ----------
        # Convert to grayscale
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Apply threshold to improve text visibility
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Resize to help OCR detect smaller fonts
        scale_percent = 150  # upscale by 1.5x
        width = int(thresh.shape[1] * scale_percent / 100)
        height = int(thresh.shape[0] * scale_percent / 100)
        resized = cv2.resize(thresh, (width, height), interpolation=cv2.INTER_LINEAR)

        # Convert back to 3-channel for EasyOCR
        processed_image = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)

        # ---------- Run OCR ----------
        results = ocr_reader.readtext(processed_image, detail=1, paragraph=False)

        if not results:
            return {"found": False, "paragraph": ""}

        # ---------- Sort results (top to bottom, left to right) ----------
        sorted_results = sorted(
            results,
            key=lambda r: (min(p[1] for p in r[0]), min(p[0] for p in r[0]))
        )

        extracted_texts = []
        for (_, text, confidence) in sorted_results:
            # Clean text to ensure numbers & symbols aren't lost
            cleaned_text = "".join(ch for ch in text if ch.isprintable())
            if cleaned_text.strip():
                extracted_texts.append(cleaned_text)

        # Merge into a paragraph
        paragraph = " ".join(extracted_texts)

        return {
            "found": True,
            "paragraph": paragraph.strip()
        }

    except Exception as e:
        logger.error(f"Error during OCR extraction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to extract text from image.")


# --- Validation handler ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Request validation error: {exc.errors()}")
    return JSONResponse(status_code=400, content={"detail": "Invalid request", "errors": exc.errors()})

# --- Reports Section ---
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class ReportStep(BaseModel):
    step_index: int
    class_id: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    imageData: Optional[str] = None
    timestamp: Optional[str] = None
    operation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ReportRequest(BaseModel):
    test_id: Optional[str] = None
    gameUrl: Optional[str] = None
    testType: Optional[str] = None
    logs: List[str] = []
    steps: List[ReportStep] = []

@app.post("/reports/generate")
async def generate_report(payload: ReportRequest):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
        from reportlab.lib.enums import TA_CENTER
        # CORRECTED: Added ImageReader to handle in-memory images
        from reportlab.lib.utils import ImageReader 
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF generator not available. Please run 'pip install reportlab'.")

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base_name = f"report_{payload.test_id or 'na'}_{ts}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, base_name)

    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story, styles = [], getSampleStyleSheet()
        
        # --- Custom Styles (condensed for brevity) ---
        title_style = ParagraphStyle('CustomTitle', parent=styles['h1'], fontSize=24, spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['h2'], fontSize=16, spaceAfter=12, spaceBefore=20, textColor=colors.darkgreen)
        info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=11, spaceAfter=6, leftIndent=20)
        log_style = ParagraphStyle('LogStyle', parent=styles['Normal'], fontSize=9, fontName='Courier', spaceAfter=2, leftIndent=10)

        # --- Cover Page & Summary ---
        story.append(Paragraph("Regulatory Compliance Test Report", title_style))
        test_info_data = [
            ['Test ID', payload.test_id or 'N/A'], 
            ['Test Type', payload.testType or 'N/A'],
            ['Generated (UTC)', ts]
        ]
        story.append(Table(test_info_data, colWidths=[4*cm, 12*cm], style=[
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey), ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        story.append(Spacer(1, 10))
        
        # Separate table for Game URL to handle long URLs properly
        if payload.gameUrl:
            url_style = ParagraphStyle('URLStyle', parent=styles['Normal'], fontSize=9, wordWrap='CJK')
            url_paragraph = Paragraph(f"<b>Game URL:</b> {payload.gameUrl}", url_style)
            story.append(url_paragraph)
            story.append(Spacer(1, 10))

        # --- Console Logs ---
        if payload.logs:
            story.append(Paragraph("Console Logs", heading_style))
            for log in payload.logs[:100]:
                story.append(Paragraph(log, log_style))
            if len(payload.logs) > 100:
                story.append(Paragraph(f"... and {len(payload.logs) - 100} more entries.", info_style))
        story.append(PageBreak())

        # --- Test Steps ---
        if payload.steps:
            story.append(Paragraph("Detailed Test Steps", heading_style))
            for step in payload.steps:
                step_title = f"Step {step.step_index}" + (f" - {step.operation}" if step.operation else "")
                story.append(Paragraph(step_title, heading_style))
                
                step_details = [['Timestamp', step.timestamp or 'N/A']]
                if step.x is not None: step_details.append(['Coordinates', f"({step.x:.1f}, {step.y:.1f})"])
                if step.class_id is not None: step_details.append(['Class ID', str(step.class_id)])
                
                story.append(Table(step_details, colWidths=[3*cm, 8*cm], style=[
                    ('BACKGROUND', (0,0), (0,-1), colors.lightblue), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
                ]))
                story.append(Spacer(1, 10))

                # CORRECTED: Image handling now uses in-memory data, avoiding temp files.
                if step.imageData:
                    try:
                        data = step.imageData.split(",", 1)[1] if "," in step.imageData else step.imageData
                        img_bytes = base64.b64decode(data)
                        img_buffer = io.BytesIO(img_bytes)
                        img_buffer.seek(0)
                        
                        # Use the image buffer directly with RLImage
                        rl_img = RLImage(img_buffer, width=16*cm, height=9*cm, kind='proportional')
                        story.append(rl_img)
                    except Exception as img_err:
                        story.append(Paragraph(f"[Image could not be rendered: {str(img_err)}]", log_style))
                
                if step.step_index < len(payload.steps):
                    story.append(PageBreak())

        doc.build(story)
        
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")

    return {"status": "success", "report_id": base_name, "url": f"/reports/{base_name}"}


# Mount static directory for serving generated reports
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")