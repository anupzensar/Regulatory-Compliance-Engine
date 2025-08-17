# ocr_helper.py

import base64
import io
from PIL import Image
import easyocr

# Initialize OCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def find_text_in_image(base64_image: str, search_text: str):
    """
    Takes a base64 image and search string.
    Returns (found: bool, x: int, y: int, matched_text: str, confidence: float)
    """
    try:
        image_bytes = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        results = reader.readtext(image)
        search = search_text.strip().lower()

        for (bbox, text, conf) in results:
            if text.strip().lower() == search:
                (tl, tr, br, bl) = bbox
                center_x = int((tl[0] + br[0]) / 2)
                center_y = int((tl[1] + br[1]) / 2)
                return True, center_x, center_y, text, conf

        return False, None, None, None, None

    except Exception as e:
        print(f"[OCR ERROR]: {e}")
        return False, None, None, None, None
