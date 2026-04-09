import fitz  # PyMuPDF
from typing import List, Dict, Any


class RawTextChunk:
    """
    Represents a chunk of raw text extracted from PDF
    """
    def __init__(self, page_num: int, text: str, start_line: int, end_line: int):
        self.page_num = page_num
        self.text = text
        self.start_line = start_line
        self.end_line = end_line


class DocumentExtractor:
    """
    Unified document extractor interface for PDF files
    Forcibly takes over low-level reading and generates a globally unified RawTextChunk[] array
    """
    def __init__(self):
        pass
    
    def extract(self, file_path: str) -> List[RawTextChunk]:
        """
        Extract text from PDF and generate RawTextChunk array
        """
        doc = fitz.open(file_path)
        chunks = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text with detailed information
            text_blocks = page.get_text("blocks")
            
            line_count = 0
            for block in text_blocks:
                block_text = block[4]  # Text content
                if block_text.strip():
                    # Split into lines
                    lines = block_text.split('\n')
                    for line in lines:
                        if line.strip():
                            start_line = line_count
                            end_line = line_count + 1
                            chunks.append(RawTextChunk(
                                page_num=page_num + 1,  # Page numbers start from 1
                                text=line.strip(),
                                start_line=start_line,
                                end_line=end_line
                            ))
                            line_count += 1
        
        doc.close()
        return chunks
    
    def get_text_from_chunks(self, chunks: List[RawTextChunk]) -> str:
        """
        Convert RawTextChunk array back to plain text
        """
        return '\n'.join([chunk.text for chunk in chunks])
    
    def get_paragraphs_from_chunks(self, chunks: List[RawTextChunk]) -> List[str]:
        """
        Convert RawTextChunk array to paragraphs
        """
        paragraphs = []
        current_paragraph = []
        
        for chunk in chunks:
            current_paragraph.append(chunk.text)
            # If the chunk ends with a period or other sentence terminator, consider it the end of a paragraph
            if chunk.text.endswith(('.', '!', '?', '。', '！', '？')):
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        # Add any remaining text as a paragraph
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return paragraphs
    
    def extract_images(self, file_path: str) -> Dict[str, bytes]:
        """
        Extract images from PDF
        """
        doc = fitz.open(file_path)
        images = {}
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                image_path = f"image_{page_num}_{img_idx}.png"
                images[image_path] = image_data
        
        doc.close()
        return images