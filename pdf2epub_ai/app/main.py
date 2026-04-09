from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import tempfile

from app.utils.pdf_processor import process_pdf
from app.config import UPLOAD_FOLDER, OUTPUT_FOLDER, LLM_ENABLED

# Create FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "llm_enabled": LLM_ENABLED})


@app.post("/convert")
async def convert(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(None),
    author: str = Form(None),
    llm_api_key: str = Form(None)
):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate output path
    output_file = os.path.join(
        OUTPUT_FOLDER,
        file.filename.replace(".pdf", ".epub")
    )
    
    # Process PDF
    success, message = process_pdf(file_path, output_file, title, author)
    
    if success:
        # Return the EPUB file
        return FileResponse(output_file, filename=os.path.basename(output_file))
    else:
        # Return error message
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": message,
            "llm_enabled": LLM_ENABLED
        })