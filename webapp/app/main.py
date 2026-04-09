from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import tempfile
import hashlib

from app.config import UPLOAD_FOLDER, OUTPUT_FOLDER, API_URL
from app.utils.pdf_processor import process_pdf
from app.utils.epub_generator import generate_epub

# Create FastAPI app FIRST
app = FastAPI()

# THEN mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert")
async def convert(
    request: Request,
    file: UploadFile = File(...),
    api_token: str = Form(...),
    title: str = Form(None),
    author: str = Form(None),
    auto_toc: bool = Form(False),
    no_toc: bool = Form(False)
):
    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp(prefix="pdf2epub_")
    file_path = os.path.join(temp_dir, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Process PDF and generate EPUB
        output_file = os.path.join(
            temp_dir,
            file.filename.replace(".pdf", ".epub")
        )

        # Call processing function
        success, message = process_pdf(
            file_path, 
            output_file, 
            api_token, 
            title, 
            author, 
            auto_toc, 
            no_toc
        )

        if not success:
            return templates.TemplateResponse(
                "index.html", 
                {"request": request, "error": message}
            )

        # Return the generated EPUB file
        return FileResponse(output_file, filename=os.path.basename(output_file))

    finally:
        # Clean up temporary files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
