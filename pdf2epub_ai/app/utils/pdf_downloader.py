import os
import requests
import hashlib
from typing import Optional, Dict, Any
from app.utils.logger import logger


class PDFDownloader:
    """
    Utility class for downloading PDF documents from URLs
    """
    def __init__(self, cache_dir: str = "./download_cache"):
        """
        Initialize PDFDownloader
        
        Args:
            cache_dir: Directory to store cached PDF files
        """
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """
        Generate cache key from URL
        
        Args:
            url: PDF URL
            
        Returns:
            Cache key as string
        """
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, url: str) -> str:
        """
        Get cache path for URL
        
        Args:
            url: PDF URL
            
        Returns:
            Cache file path
        """
        cache_key = self._get_cache_key(url)
        return os.path.join(self.cache_dir, f"{cache_key}.pdf")
    
    def download(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Download PDF from URL
        
        Args:
            url: PDF URL
            timeout: Request timeout in seconds
            
        Returns:
            Path to downloaded PDF file, or None if download failed
        """
        try:
            # Check if PDF is already cached
            cache_path = self._get_cache_path(url)
            if os.path.exists(cache_path):
                logger.info(f"PDF already cached: {cache_path}")
                return cache_path
            
            logger.info(f"Downloading PDF from: {url}")
            
            # Send HTTP request with SSL verification disabled (for testing)
            response = requests.get(url, timeout=timeout, stream=True, verify=False)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Check if response is PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"Response is not PDF: {content_type}")
                return None
            
            # Save to cache
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"PDF downloaded successfully: {cache_path}")
            return cache_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
    
    def clear_cache(self) -> bool:
        """
        Clear all cached PDF files
        
        Returns:
            True if cache was cleared successfully
        """
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.pdf'):
                    os.remove(os.path.join(self.cache_dir, file))
            logger.info("Cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache information
        
        Returns:
            Dictionary with cache info
        """
        try:
            files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pdf')]
            total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
            
            return {
                "cache_dir": self.cache_dir,
                "file_count": len(files),
                "total_size": total_size,
                "files": files
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {str(e)}")
            return {"error": str(e)}
