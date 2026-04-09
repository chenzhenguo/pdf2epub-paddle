import os
import sys
import tempfile
import re

import fitz  # PyMuPDF
from ebooklib import epub
from typing import List, Dict, Any

from app.config import CHUNK_SIZE, MAX_DAILY_PAGES


def extract_pdf_content(file_path: str) -> tuple:
    """
    Extract text and images from PDF file using PyMuPDF
    Returns (text, images) where images is a dict of {path: data}
    """
    doc = fitz.open(file_path)
    text = ""
    images = {}
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Extract text
        page_text = page.get_text()
        text += page_text + "\n\n"
        
        # Extract images
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            image_path = f"image_{page_num}_{img_idx}.png"
            images[image_path] = image_data
    
    doc.close()
    return text, images


def clean_text(text: str) -> List[str]:
    """
    Clean extracted text and split into paragraphs
    """
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    
    # Clean each paragraph
    cleaned_paragraphs = []
    for para in paragraphs:
        # Remove leading/trailing whitespace
        para = para.strip()
        
        # Remove page numbers
        para = re.sub(r'^\d+$', '', para)
        
        # Remove excessive spaces
        para = re.sub(r'\s{2,}', ' ', para)
        
        if para:
            cleaned_paragraphs.append(para)
    
    return cleaned_paragraphs


def detect_book_structure(paragraphs: List[str]) -> Dict:
    """
    Detect book structure using simple heuristics (to be replaced with LLM)
    """
    structure = {
        "title": None,
        "author": None,
        "chapters": []
    }
    
    # Simple title detection (first few paragraphs)
    if paragraphs:
        structure["title"] = paragraphs[0]
        
        # Simple author detection (second paragraph if it looks like an author)
        if len(paragraphs) > 1:
            author_candidates = paragraphs[1]
            # Check if it looks like an author name (contains common title words)
            author_pattern = re.compile(r'(by|author|written by)', re.IGNORECASE)
            if author_pattern.search(author_candidates):
                structure["author"] = author_candidates
    
    # Simple chapter detection
    chapter_pattern = re.compile(r'^(chapter|part|section)\s+\d+', re.IGNORECASE)
    current_chapter = None
    
    for i, para in enumerate(paragraphs):
        if chapter_pattern.match(para):
            if current_chapter:
                structure["chapters"].append(current_chapter)
            current_chapter = {
                "title": para,
                "start_idx": i
            }
    
    if current_chapter:
        structure["chapters"].append(current_chapter)
    
    return structure


def map_sections_to_content(paragraphs: List[str], structure: Dict) -> List[tuple]:
    """
    Map detected sections to actual content
    """
    sections = []
    
    # Add title and author as front matter
    front_matter = []
    if structure["title"]:
        front_matter.append(structure["title"])
    if structure["author"]:
        front_matter.append(structure["author"])
    
    if front_matter:
        sections.append(("Front Matter", front_matter))
    
    # Add chapters
    chapters = structure.get("chapters", [])
    for i, chapter in enumerate(chapters):
        start_idx = chapter["start_idx"]
        end_idx = chapters[i+1]["start_idx"] if i < len(chapters) - 1 else len(paragraphs)
        chapter_content = paragraphs[start_idx:end_idx]
        sections.append((chapter["title"], chapter_content))
    
    # If no chapters detected, add all content as one chapter
    if not chapters and paragraphs:
        sections.append(("Content", paragraphs))
    
    return sections


def format_paragraph(paragraph: str) -> str:
    """
    Format paragraph for EPUB
    """
    # Add proper spacing and formatting
    return paragraph


def process_pdf(
    input_path: str, 
    output_path: str, 
    api_token: str, 
    title: str = None, 
    author: str = None, 
    auto_toc: bool = False, 
    no_toc: bool = False
) -> tuple:
    """
    Process PDF file and generate EPUB
    Returns (success, message)
    """
    try:
        # Step 1: Extract content from PDF
        print("[-] Step 1: Extracting PDF content...")
        text, images = extract_pdf_content(input_path)
        
        # Step 2: Clean and process text
        print("[-] Step 2: Cleaning and processing text...")
        paragraphs = clean_text(text)
        
        # Step 3: Detect book structure
        print("[-] Step 3: Detecting book structure...")
        structure = detect_book_structure(paragraphs)
        sections = map_sections_to_content(paragraphs, structure)
        
        # Step 4: Format paragraphs
        print("[-] Step 4: Formatting content...")
        formatted_chapters = []
        for section_title, section_content in sections:
            formatted_content = [format_paragraph(p) for p in section_content]
            formatted_chapters.append((section_title, formatted_content))
        
        # Step 5: Generate EPUB
        print("[-] Step 5: Generating EPUB...")
        from app.utils.epub_generator import generate_epub
        generate_epub(formatted_chapters, images, output_path)
        
        return True, "Conversion completed successfully"

    except Exception as e:
        print(f"[!] Error during processing: {e}")
        return False, f"An error occurred: {str(e)}"
