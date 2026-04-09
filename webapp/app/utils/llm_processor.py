import os
import requests
import json
from typing import List, Dict, Any

class LLMProcessor:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize LLM processor
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def detect_book_structure(self, paragraphs: List[str]) -> Dict:
        """
        Use LLM to detect book structure
        """
        # Prepare prompt
        prompt = f"""You are an expert in book structure analysis. Analyze the following text and identify:
        1. Book title
        2. Author name
        3. Chapters with their titles and start positions

        Text:
        {"\n\n".join(paragraphs[:50])}  # First 50 paragraphs for analysis

        Return the result as a JSON object with the following structure:
        {
            "title": "Book Title",
            "author": "Author Name",
            "chapters": [
                {
                    "title": "Chapter 1 Title",
                    "start_idx": 5
                },
                ...
            ]
        }
        """
        
        # Call OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert in book structure analysis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Parse response
            structure = json.loads(result["choices"][0]["message"]["content"])
            return structure
        except Exception as e:
            print(f"[!] LLM structure detection failed: {e}")
            # Fallback to heuristic method
            from app.utils.pdf_processor import detect_book_structure
            return detect_book_structure(paragraphs)
    
    def format_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """
        Use LLM to format paragraphs for better readability
        """
        # Prepare prompt
        prompt = f"""You are an expert in text formatting. Format the following paragraphs for better readability in an EPUB book:
        
        {"\n\n".join(paragraphs[:20])}  # First 20 paragraphs for formatting
        
        Guidelines:
        1. Fix any grammatical errors
        2. Ensure proper punctuation
        3. Improve sentence structure if needed
        4. Maintain the original meaning
        5. Return each paragraph on a separate line
        """
        
        # Call OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert in text formatting."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Parse response
            formatted_text = result["choices"][0]["message"]["content"]
            formatted_paragraphs = [p.strip() for p in formatted_text.split("\n") if p.strip()]
            return formatted_paragraphs
        except Exception as e:
            print(f"[!] LLM paragraph formatting failed: {e}")
            # Fallback to original paragraphs
            return paragraphs
    
    def generate_toc(self, structure: Dict) -> List[Dict]:
        """
        Use LLM to generate a more comprehensive table of contents
        """
        # Prepare prompt
        prompt = f"""You are an expert in book formatting. Based on the following book structure, generate a comprehensive table of contents:
        
        {json.dumps(structure, indent=2)}
        
        Guidelines:
        1. Ensure all chapters are included
        2. Add appropriate hierarchy if needed
        3. Return the result as a JSON array of objects with title and start_idx
        """
        
        # Call OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert in book formatting."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Parse response
            toc = json.loads(result["choices"][0]["message"]["content"])
            return toc
        except Exception as e:
            print(f"[!] LLM TOC generation failed: {e}")
            # Fallback to original structure
            return structure.get("chapters", [])
