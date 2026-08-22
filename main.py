import os
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from PIL import Image
from pix2tex.cli import LatexOCR

app = FastAPI()

# 1. Load the model ONCE globally at startup
print("Loading Pix2Tex LaTeX-OCR model into memory...")
ocr_model = LatexOCR()
print("Model loaded successfully!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(BASE_DIR, "client")

# Define Data Model
class ImagePayload(BaseModel):
    image: str  # Base64 image from app.js

# 2. Define API Endpoints FIRST

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

        # Convert Base64 bytes to PIL Image
        image_bytes = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(image_bytes))

        # Predict LaTeX string using pre-loaded model
        latex_string = ocr_model(img)
        
        print("\n" + "="*40)
        print(" [Pix2Tex Result]:", latex_string)
        print("="*40 + "\n")

        return {"latex": latex_string}

    except Exception as e:
        print(f"[OCR Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. Mount static files AFTER API endpoints
app.mount("", StaticFiles(directory=CLIENT_DIR, html=True), name="client")

# 4. Server Execution block LAST
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)