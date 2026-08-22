from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(BASE_DIR, "client")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(CLIENT_DIR, "index.html"))

# Mount static files (CSS, JS, images, etc.)
app.mount("", StaticFiles(directory=CLIENT_DIR, html=True), name="client")

# Serve index.html at the root URL '/'
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(CLIENT_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    # Host on 0.0.0.0 to listen on all local network interfaces
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)