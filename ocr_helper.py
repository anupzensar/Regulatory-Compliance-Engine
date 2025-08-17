# ocr_helper.py
import base64
import sys
import json
from PIL import Image
import io
import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

def find_text(base64_img, query_text):
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    np_image = np.array(image)

    results = reader.readtext(np_image)

    query = query_text.strip().lower()

    for (bbox, text, confidence) in results:
        if query in text.strip().lower():
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            x_center = int(sum(x_coords) / len(x_coords))
            y_center = int(sum(y_coords) / len(y_coords))

            return {
                "found": True,
                "text": text,
                "x": x_center,
                "y": y_center,
                "confidence": round(confidence * 100, 2)
            }

    return {"found": False}


if __name__ == "__main__":
    try:
        input_data = sys.stdin.read()
        payload = json.loads(input_data)
        base64_image = payload.get("image")
        query = payload.get("query")

        result = find_text(base64_image, query)
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"found": False, "error": str(e)}))
