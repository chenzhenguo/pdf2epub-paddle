import json
import os
import concurrent.futures
from typing import List, Dict, Any
from openai import OpenAI

from app.utils.logger import logger


class LLMProcessor:
    """
    LLM processor for book structure detection and text formatting
    """
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    def detect_book_structure(self, paragraphs: List[str]) -> Dict:
        """
        Uses LLM to detect chapters and front matter.
        Returns structured list of sections.
        """
        # Limit size to avoid token explosion
        sample_text = "\n\n".join(paragraphs[:200])
        
        prompt = f"""
        You are a book structure parser.
        
        Analyze the following book text and detect:
        
        - Front matter sections (copyright, dedication, etc.)
        - Real chapter titles
        - The start of each chapter
        
        Return JSON only in this format:
        
        {{
          "title": "Book Title",
          "author": "Author Name",
          "chapters": [
            {{
              "title": "Chapter Title",
              "start_idx": 0
            }}
          ]
        }}
        
        Text:
        {sample_text}
        """
        
        try:
            logger.info("Detecting book structure using LLM...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            structure = json.loads(result)
            
            # Convert chapter start indices to integers
            for chapter in structure.get("chapters", []):
                if "start_idx" in chapter:
                    chapter["start_idx"] = int(chapter["start_idx"])
            
            logger.info("Book structure detected successfully")
            return structure
            
        except Exception as e:
            logger.error("LLM error during structure detection: %s", str(e))
            # Fallback: treat entire book as one section
            fallback_structure = {
                "title": paragraphs[0] if paragraphs else "Unknown Title",
                "author": "Unknown Author",
                "chapters": [
                    {
                        "title": "Book",
                        "start_idx": 0
                    }
                ]
            }
            logger.warning("Falling back to basic structure detection")
            return fallback_structure
    
    def format_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """
        Uses LLM to format paragraphs for better readability
        """
        formatted_paragraphs = []
        
        # Process paragraphs in batches to reduce API calls
        batch_size = 10
        for i in range(0, len(paragraphs), batch_size):
            batch = paragraphs[i:i+batch_size]
            batch_text = "\n\n".join(batch)
            
            prompt = f"""
            You are a text formatter. Format the following paragraphs for better readability in an EPUB book.
            
            For each paragraph:
            1. Add proper HTML paragraph tags
            2. Preserve the original content
            3. Add appropriate CSS classes if needed
            4. Return each paragraph on a separate line
            
            Example output:
            <p class="para">This is a formatted paragraph.</p>
            <p class="para">This is another formatted paragraph.</p>
            
            Paragraphs:
            {batch_text}
            """
            
            try:
                logger.info(f"Formatting batch {i//batch_size + 1} of {len(paragraphs)//batch_size + 1}...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=2000
                )
                
                result = response.choices[0].message.content
                formatted_batch = result.strip().split('\n')
                formatted_paragraphs.extend(formatted_batch)
                logger.info(f"Batch {i//batch_size + 1} formatted successfully")
                
            except Exception as e:
                logger.error(f"LLM formatting error for batch {i//batch_size + 1}: %s", str(e))
                # Fallback: basic formatting
                for para in batch:
                    formatted_paragraphs.append(f'<p class="para">{para}</p>')
                logger.warning(f"Falling back to basic formatting for batch {i//batch_size + 1}")
        
        logger.info(f"Formatted {len(formatted_paragraphs)} paragraphs")
        return formatted_paragraphs
    
    def format_paragraphs_parallel(self, paragraphs: List[str]) -> List[str]:
        """
        Uses parallel processing to format paragraphs
        """
        formatted_paragraphs = []
        
        def process_batch(batch):
            return self.format_paragraphs(batch)
        
        # Split into batches
        batch_size = 10
        batches = [paragraphs[i:i+batch_size] for i in range(0, len(paragraphs), batch_size)]
        
        # Process batches in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(process_batch, batches)
            
            for batch_result in results:
                formatted_paragraphs.extend(batch_result)
        
        return formatted_paragraphs