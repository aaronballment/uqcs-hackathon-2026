import os
import re
import base64
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import graphing

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

print("Initializing Gemini Client...")
gemini_client = genai.Client()
print("Gemini Client ready!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(BASE_DIR, "client")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

os.makedirs(PLOTS_DIR, exist_ok=True)

# Add x_min and x_max to the Pydantic model with default fallback values
class ImagePayload(BaseModel):
    image: str
    x_min: float = -10.0
    x_max: float = 10.0

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(CLIENT_DIR, "index.html"))

@app.post("/api/extract-math")
async def extract_math(payload: ImagePayload):
    try:
        # Extract base64 and determine mime type safely
        if "," in payload.image:
            header, base64_data = payload.image.split(",", 1)
            mime_match = re.search(r'data:(.*?);base64', header)
            mime_type = mime_match.group(1) if mime_match else "image/jpeg"
        else:
            base64_data = payload.image
            mime_type = "image/jpeg"

        image_bytes = base64.b64decode(base64_data)

        prompt = (
            "You are an expert mathematical OCR tool. "
            "Extract the primary handwritten function or expression from the image. "
            "Return ONLY the LaTeX string suitable for parsing (e.g., x^2 - 4 or 2*x + 1). "
            "do not include the variable axis only the equation example if y=x^2 return x^2"
            "Do not include markdown code blocks, backticks, explanations, or label headers."
        )

        response = gemini_client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )

        extracted_text = response.text.strip()
        extracted_text = re.sub(r'^```(?:latex)?|```$', '', extracted_text, flags=re.MULTILINE).strip()

        print("\n" + "="*40)
        print(" [Gemini Result]:", extracted_text)
        print("="*40 + "\n")

        safe_filename = re.sub(r'[/\\:*?"<>|]', '_', extracted_text).strip()
        if not safe_filename:
            safe_filename = "output_plot"
        filename = f"{safe_filename}.png"
        clean_filename = os.path.basename(filename)

        try: 
            print(f"Extracted math: {extracted_text}")
            # Access values directly from payload
            graphing.latex_conversion(extracted_text, clean_filename, payload.x_min, payload.x_max)
        except Exception as e:
            print(f"[Graphing Error]: {e}")
            return {
                "error": f"Extracted '{extracted_text}', but failed to plot image.",
                "latex": extracted_text
            }

        return {"latex": extracted_text, "filename": clean_filename}

    except Exception as e:
        print(f"[OCR Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/plots", StaticFiles(directory=PLOTS_DIR), name="plots")
app.mount("", StaticFiles(directory=CLIENT_DIR, html=True), name="client")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)