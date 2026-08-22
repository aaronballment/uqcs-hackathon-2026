import os
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import vision  # Import Google Cloud Vision SDK

app = FastAPI()

# 1. Initialize Google Cloud Vision Client globally
# It automatically picks up credentials from GOOGLE_APPLICATION_CREDENTIALS env var
print("Initializing Google Cloud Vision Client...")
vision_client = vision.ImageAnnotatorClient()
print("Vision Client ready!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(BASE_DIR, "client")

class ImagePayload(BaseModel):
    image: str  # Base64 image string from front-end

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(CLIENT_DIR, "index.html"))

@app.post("/api/extract-math")
async def extract_math(payload: ImagePayload):
    try:
        # Strip Base64 header if present
        if "," in payload.image:
            base64_data = payload.image.split(",")[1]
        else:
            base64_data = payload.image

        # Decode Base64 string directly to raw bytes
        image_bytes = base64.b64decode(base64_data)

        # Build Vision API Image object from bytes
        vision_image = vision.Image(content=image_bytes)

        # Call Document Text Detection (optimized for dense text & equations)
        response = vision_client.document_text_detection(image=vision_image)

        # Handle API Errors
        if response.error.message:
            raise Exception(f"Google Vision API Error: {response.error.message}")

        # Extract text annotations
        extracted_text = response.full_text_annotation.text if response.full_text_annotation else ""

        # Clean up whitespace/newlines
        extracted_text = extracted_text.strip()

        print("\n" + "="*40)
        print(" [Google Vision Result]:", extracted_text)
        print("="*40 + "\n")

        # Return key matching your front-end expectation
        return {"latex": extracted_text}

    except Exception as e:
        print(f"[OCR Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("", StaticFiles(directory=CLIENT_DIR, html=True), name="client")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)