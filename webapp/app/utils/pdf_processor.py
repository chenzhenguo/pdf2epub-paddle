import os
import sys
import json
import tempfile
import base64
import re

import requests
import fitz  # PyMuPDF
from ebooklib import epub
from typing import List, Dict, Any

from app.config import API_URL, CHUNK_SIZE, MAX_DAILY_PAGES

def split_pdf(file_path: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Splits a PDF into chunks of `chunk_size` pages.
    Returns a list of paths to the temporary chunk files.
    """
    doc = fitz.open(file_path)
    total_pages = len(doc)
    print(f"[*] Total pages: {total_pages}")

    if total_pages > MAX_DAILY_PAGES:
        print(
            f"[!] WARNING: This document ({total_pages} pages) exceeds the daily API limit of {MAX_DAILY_PAGES} pages."
        )
        print("    Processing may fail or get blocked if you exceed your quota.")

    chunk_paths = []
    temp_dir = tempfile.mkdtemp(prefix="pdf_chunks_")

    for start_page in range(0, total_pages, chunk_size):
        end_page = min(start_page + chunk_size, total_pages)
        # Create a new PDF for this chunk
        chunk_doc = fitz.open()
        chunk_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)

        chunk_filename = os.path.join(temp_dir, f"chunk_{start_page}_{end_page}.pdf")
        chunk_doc.save(chunk_filename)
        chunk_doc.close()
        chunk_paths.append(chunk_filename)

    doc.close()
    return chunk_paths


def parse_pdf_chunk(chunk_path: str, token: str) -> Dict[str, Any]:
    """
    Sends a PDF chunk to the PaddleOCR API and returns the parsed result.
    """
    print(f"[*] uploading chunk: {os.path.basename(chunk_path)}")

    with open(chunk_path, "rb") as file:
        file_bytes = file.read()
        file_data = base64.b64encode(file_bytes).decode("ascii")

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}

    payload = {
        "file": file_data,
        "fileType": 0,  # 0 for PDF
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,  # Basic extraction
    }

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL, json=payload, headers=headers, timeout=180
            )
            response.raise_for_status()
            result = response.json()

            # Handle API responses safely
            if "error" in result:
                print(
                    f"[!] API Error for chunk {os.path.basename(chunk_path)}: {result['error']}"
                )
                return None

            return result

        except (requests.exceptions.RequestException, ConnectionError) as e:
            wait_time = (
                2**attempt
            ) * 5  # Exponential backoff: 5, 10, 20, 40, 80 seconds
            print(f"[!] API Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"    Retrying in {wait_time}s...")
                import time
                time.sleep(wait_time)
            else:
                print(
                    f"[!] Permanently failed processing chunk: {os.path.basename(chunk_path)}"
                )
                return None
        except Exception as e:
            print(
                f"[!] Unexpected error processing chunk {os.path.basename(chunk_path)}: {e}"
            )
            return None


def extract_cover_image(pdf_path: str, output_path: str) -> str:
    """Renders the first page of a PDF as a PNG image for use as an EPUB cover."""
    doc = fitz.open(pdf_path)
    try:
        if len(doc) == 0:
            print("[!] PDF has no pages; skipping cover extraction.")
            return None
        page = doc.load_page(0)
        mat = fitz.Matrix(2, 2)  # 2x zoom (~144 DPI)
        pix = page.get_pixmap(matrix=mat)
        pix.save(output_path)
        print(f"[*] Cover image extracted to {output_path}")
        return output_path
    except Exception as e:
        print(f"[!] Failed to extract cover image: {e}")
        return None
    finally:
        doc.close()


def extract_candidate_headings(results: List[Dict]) -> List[Dict]:
    """Scans API results and extracts candidate chapter headings with page numbers."""
    candidates = []
    any_header_pattern = re.compile(r"^(#{1,2})\s+(.+)$")
    latex_pattern = re.compile(r"\$\s*\\underline\{(.+?)\}\s*\$")
    global_page = 0

    for result in results:
        if not result or "result" not in result:
            continue
        for page_res in result["result"].get("layoutParsingResults", []):
            global_page += 1
            page_md = page_res["markdown"]["text"]
            for line in page_md.split("\n"):
                if line.strip().isdigit():
                    continue
                match = any_header_pattern.match(line)
                if match:
                    title = match.group(2).strip()
                    # Clean LaTeX artifacts
                    title = latex_pattern.sub("", title).strip()
                    # Strip leading bare numbers
                    title = re.sub(r"^\d+\s+", "", title).strip()
                    candidates.append({
                        "title": title,
                        "page": global_page,
                        "level": len(match.group(1)),
                        "md_line": line,
                    })
    return candidates


def filter_heading_candidates(candidates: List[Dict]) -> List[Dict]:
    """Adaptively filters headings by trying H1-only, then keyword match, then all."""
    chapter_keyword = re.compile(
        r"^(?:Chapter|Part|Lecture|Preface|Intro|Appendix|Prologue|Epilogue|" 
        r"Conclusion|Acknowledgements|Contents|Abstract|序|前言|导论|目录|附录|后记|" 
        r"第[零一二三四五六七八九十百千0-9]+[篇章节讲])",
        re.IGNORECASE,
    )

    # Strategy 1: H1-only (skip front-matter on first 2 pages)
    h1 = [h for h in candidates if h["level"] == 1 and h["page"] > 2]
    if len(h1) >= 4:
        return h1

    # Strategy 2: Keyword-matched headings (any level)
    keyword_matches = [h for h in candidates if chapter_keyword.match(h["title"])]
    if len(keyword_matches) >= 3:
        return keyword_matches

    # Strategy 3: All headings (last resort)
    return candidates

def download_image(url: str, save_path: str):
    """Downloads an image from a URL to a local path."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"[!] Failed to download image {url}: {e}")
    return False

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
        # Create work directory
        work_dir = tempfile.mkdtemp(prefix="paddle_epub_work_")
        image_dir = os.path.join(work_dir, "images")
        os.makedirs(image_dir, exist_ok=True)

        # Step 1: Chunking
        print("[-] Step 1: Splitting PDF...")
        chunk_paths = split_pdf(input_path)

        # Step 1.5: Extract cover image
        cover_path = extract_cover_image(input_path, os.path.join(work_dir, "cover.png"))

        # Step 2: API Processing
        results = []
        print(f"[-] Step 2: Processing {len(chunk_paths)} chunks via PaddleOCR API...")
        for i, chunk in enumerate(chunk_paths):
            chunk_name = os.path.basename(chunk)
            json_checkpoint = os.path.join(work_dir, chunk_name + ".json")

            if os.path.exists(json_checkpoint):
                print(
                    f"    [+] Resuming: Found checkpoint for chunk {i + 1}/{len(chunk_paths)}"
                )
                with open(json_checkpoint, "r") as f:
                    res = json.load(f)
            else:
                # Rate limiting: Sleep before new request
                if i > 0:
                    print("    ...waiting 5s to respect API rate limits...")
                    import time
                    time.sleep(5)

                print(f"    Processing chunk {i + 1}/{len(chunk_paths)}...")
                res = parse_pdf_chunk(chunk, api_token)

                if res:
                    # Save checkpoint
                    os.makedirs(os.path.dirname(json_checkpoint), exist_ok=True)
                    with open(json_checkpoint, "w") as f:
                        json.dump(res, f)

            if res:
                results.append(res)

                # Download images immediately to save locally
                layout_results = res.get("result", {}).get("layoutParsingResults", [])
                for page_res in layout_results:
                    images_map = page_res["markdown"].get("images", {})
                    for rel_path, img_url in images_map.items():
                        local_path = os.path.join(image_dir, rel_path)
                        if not os.path.exists(local_path):  # Don't re-download if exists
                            download_image(img_url, local_path)
            else:
                return False, f"Failed to process chunk {i + 1}. Please check your API token and network connection."

        # Step 2.5: Metadata extraction
        default_title = os.path.splitext(os.path.basename(input_path))[0]
        if not title:
            title = default_title

        # Step 2.75: TOC Review
        if no_toc:
            confirmed_headings = []
        elif auto_toc:
            confirmed_headings = None
        else:
            print("[-] Step 2.75: Detecting chapter headings...")
            candidates = extract_candidate_headings(results)
            filtered = filter_heading_candidates(candidates)
            confirmed_headings = filtered

        # Step 3: Generation
        print("[-] Step 3: Generating EPUB...")
        from app.utils.epub_generator import create_epub
        create_epub(
            title, 
            results, 
            output_path, 
            image_dir, 
            cover_image_path=cover_path, 
            author=author, 
            confirmed_headings=confirmed_headings
        )

        return True, "Conversion completed successfully"

    except Exception as e:
        print(f"[!] Error during processing: {e}")
        return False, f"An error occurred: {str(e)}"
    finally:
        # Clean up
        if 'work_dir' in locals() and os.path.exists(work_dir):
            import shutil
            shutil.rmtree(work_dir)
