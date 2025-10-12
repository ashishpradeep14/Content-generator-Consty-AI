from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pathlib import Path
from typing import Optional
import os
import time

from app.schemas import ContentRequest
from generator import RobustContentGenerator

app = FastAPI(title="Robust Content Generator API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Initialize generator
generator = RobustContentGenerator()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main UI page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=JSONResponse)
async def generate_content(
    request: Request,
    prompt: str = Form(...),
    content_type: str = Form("summary"),
):
    """Generate content based on user input"""
    start_time = time.time()
    
    try:
        result = generator.generate_content(prompt, content_type)
        
        if "error" in result:
            return JSONResponse(
                {"error": result["error"]},
                status_code=400
            )
            
        processing_time = round(time.time() - start_time, 2)
        result["processing_time"] = processing_time
        
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse(
            {"error": f"Generation failed: {str(e)}"},
            status_code=500
        )

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    """Download generated PDF"""
    file_path = Path("output") / filename
    if not file_path.exists():
        return JSONResponse(
            {"error": "File not found"},
            status_code=404
        )
    return FileResponse(file_path, filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)