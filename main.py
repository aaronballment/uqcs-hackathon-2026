import os
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import vision  # Import Google Cloud Vision SDK
import graphing

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

print("Initializing Google Cloud Vision Client...")
vision_client = vision.ImageAnnotatorClient()
print("Vision Client ready!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(BASE_DIR, "client")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

# Ensure the plots directory exists
os.makedirs(PLOTS_DIR, exist_ok=True)

class ImagePayload(BaseModel):
    image: str

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(CLIENT_DIR, "index.html"))

@app.post("/api/extract-math")
async def extract_math(payload: ImagePayload):
    try:
        if "," in payload.image:
            base64_data = payload.image.split(",")[1]
        else:
            base64_data = payload.image

        image_bytes = base64.b64decode(base64_data)
        vision_image = vision.Image(content=image_bytes)

        response = vision_client.document_text_detection(image=vision_image)

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
        try: 
            graphing.latex_conversion(extracted_text,extracted_text)
        except Exception as e:
            print(f"[Graphing Error]: {e}")

        return {"latex": extracted_text, "filename": filename}

    except Exception as e:
        print(f"[OCR Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 1. Mount the /plots endpoint to expose the plots/ folder to the browser
app.mount("/plots", StaticFiles(directory=PLOTS_DIR), name="plots")

# 2. Mount client directory for static frontend files
app.mount("", StaticFiles(directory=CLIENT_DIR, html=True), name="client")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)