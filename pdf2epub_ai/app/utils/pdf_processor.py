import os
import re
from typing import List, Dict, Any, Tuple

from app.utils.document_extractor import DocumentExtractor, RawTextChunk
from app.utils.logger import logger
from app.config import LLM_ENABLED, LLM_API_KEY, LLM_MODEL

if LLM_ENABLED:
    from app.utils.llm_processor import LLMProcessor


def extract_pdf_content(file_path: str) -> Tuple[str, Dict[str, bytes]]:
    """
    Extract text and images from PDF file using DocumentExtractor
    Returns (text, images) where images is a dict of {path: data}
    """
    # Use DocumentExtractor for text extraction
    extractor = DocumentExtractor()
    chunks = extractor.extract(file_path)
    text = extractor.get_text_from_chunks(chunks)
    images = extractor.extract_images(file_path)
    
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
    return f'<p class="para">{paragraph}</p>'


def process_pdf(
    input_path: str, 
    output_path: str, 
    title: str = None, 
    author: str = None
) -> Tuple[bool, str]:
    """
    Process PDF file and generate EPUB
    Returns (success, message)
    """
    try:
        logger.info("Starting PDF processing: %s", input_path)
        
        # Step 1: Extract content from PDF using DocumentExtractor
        logger.info("Step 1: Extracting PDF content...")
        try:
            extractor = DocumentExtractor()
            chunks = extractor.extract(input_path)
            text = extractor.get_text_from_chunks(chunks)
            images = extractor.extract_images(input_path)
            logger.info("Extracted %d text chunks and %d images", len(chunks), len(images))
        except Exception as e:
            logger.error("Error during PDF extraction: %s", str(e))
            return False, f"Error extracting PDF content: {str(e)}"
        
        # Step 2: Get paragraphs from chunks
        logger.info("Step 2: Processing text...")
        try:
            paragraphs = extractor.get_paragraphs_from_chunks(chunks)
            logger.info("Processed %d paragraphs", len(paragraphs))
        except Exception as e:
            logger.error("Error processing text: %s", str(e))
            return False, f"Error processing text: {str(e)}"
        
        # Step 3: Detect book structure
        logger.info("Step 3: Detecting book structure...")
        try:
            if LLM_ENABLED and LLM_API_KEY:
                logger.info("Using LLM for structure detection...")
                llm_processor = LLMProcessor(LLM_API_KEY, LLM_MODEL)
                structure = llm_processor.detect_book_structure(paragraphs)
            else:
                logger.info("Using heuristic structure detection...")
                structure = detect_book_structure(paragraphs)
            logger.info("Detected structure: title='%s', author='%s', chapters=%d", 
                      structure.get("title", "Unknown"), 
                      structure.get("author", "Unknown"), 
                      len(structure.get("chapters", [])))
        except Exception as e:
            logger.error("Error detecting book structure: %s", str(e))
            # Fallback to basic structure
            structure = {
                "title": title or paragraphs[0] if paragraphs else "Unknown Title",
                "author": author or "Unknown Author",
                "chapters": [{
                    "title": "Book",
                    "start_idx": 0
                }]
            }
            logger.warning("Falling back to basic structure detection")
        
        # Override title and author if provided
        if title:
            structure["title"] = title
        if author:
            structure["author"] = author
        
        sections = map_sections_to_content(paragraphs, structure)
        
        # Step 4: Format paragraphs
        logger.info("Step 4: Formatting content...")
        formatted_chapters = []
        try:
            for section_title, section_content in sections:
                if LLM_ENABLED and LLM_API_KEY and len(section_content) > 0:
                    logger.info("Using LLM to format %s...", section_title)
                    llm_processor = LLMProcessor(LLM_API_KEY, LLM_MODEL)
                    formatted_content = llm_processor.format_paragraphs(section_content)
                else:
                    formatted_content = [format_paragraph(p) for p in section_content]
                formatted_chapters.append((section_title, formatted_content))
            logger.info("Formatted %d chapters", len(formatted_chapters))
        except Exception as e:
            logger.error("Error formatting content: %s", str(e))
            # Fallback to basic formatting
            formatted_chapters = [(title, [format_paragraph(p) for p in paragraphs])]
            logger.warning("Falling back to basic text formatting")
        
        # Step 5: Generate EPUB
        logger.info("Step 5: Generating EPUB...")
        try:
            from app.utils.epub_generator import generate_epub
            generate_epub(formatted_chapters, images, output_path, structure)
            logger.info("EPUB generated successfully: %s", output_path)
        except Exception as e:
            logger.error("Error generating EPUB: %s", str(e))
            return False, f"Error generating EPUB: {str(e)}"
        
        return True, "Conversion completed successfully"

    except Exception as e:
        logger.error("Unexpected error during processing: %s", str(e))
        return False, f"An unexpected error occurred: {str(e)}"