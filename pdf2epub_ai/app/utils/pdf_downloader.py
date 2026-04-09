import os
import requests
import hashlib
import time
from typing import Optional, Dict, Any, Union
from app.utils.logger import logger


class PDFDownloader:
    """
    Robust PDF downloader with support for different sources, caching, and retry mechanism
    
    Features:
    - Download PDFs from URLs with automatic caching
    - Support for local files and cloud storage paths (placeholder)
    - Network failure retry with exponential backoff
    - Comprehensive error handling
    - Cache management utilities
    """
    def __init__(self, cache_dir: str = "./download_cache", max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize PDFDownloader
        
        Args:
            cache_dir: Directory to store cached PDF files
            max_retries: Maximum number of retry attempts for network failures
            retry_delay: Initial delay in seconds between retries
        """
        self.cache_dir = cache_dir
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """
        Generate cache key from URL
        
        Args:
            url: PDF URL
            
        Returns:
            Cache key as string
        """
        try:
            return hashlib.md5(url.encode()).hexdigest()
        except (UnicodeEncodeError, TypeError) as e:
            logger.error(f"Error generating cache key: {str(e)}")
            raise ValueError(f"Invalid URL for cache key generation: {url}")
    
    def _get_cache_path(self, url: str) -> str:
        """
        Get cache path for URL
        
        Args:
            url: PDF URL
            
        Returns:
            Cache file path
        """
        try:
            cache_key = self._get_cache_key(url)
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.pdf")
            return cache_path
        except Exception as e:
            logger.error(f"Error generating cache path: {str(e)}")
            raise ValueError(f"Failed to generate cache path for URL: {url}")
    
    def download(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Download PDF from URL with retry mechanism
        
        Args:
            url: PDF URL
            timeout: Request timeout in seconds
            
        Returns:
            Path to downloaded PDF file, or None if download failed
        """
        # Check if PDF is already cached
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            logger.info(f"PDF already cached: {cache_path}")
            return cache_path
        
        logger.info(f"Downloading PDF from: {url}")
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
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
                retry_count += 1
                if retry_count > self.max_retries:
                    logger.error(f"Error downloading PDF after {self.max_retries} retries: {str(e)}")
                    return None
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** (retry_count - 1))
                logger.warning(f"Download failed (attempt {retry_count}/{self.max_retries}), retrying in {delay}s: {str(e)}")
                time.sleep(delay)
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
            if not os.path.exists(self.cache_dir):
                logger.info("Cache directory does not exist, nothing to clear")
                return True
            
            files_removed = 0
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                if file.endswith('.pdf') and os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        files_removed += 1
                    except (PermissionError, OSError) as e:
                        logger.error(f"Error removing file {file}: {str(e)}")
            
            logger.info(f"Cache cleared successfully, removed {files_removed} files")
            return True
        except (PermissionError, OSError) as e:
            logger.error(f"Error accessing cache directory: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error clearing cache: {str(e)}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache information
        
        Returns:
            Dictionary with cache info
        """
        try:
            if not os.path.exists(self.cache_dir):
                return {
                    "cache_dir": self.cache_dir,
                    "file_count": 0,
                    "total_size": 0,
                    "files": [],
                    "status": "Cache directory does not exist"
                }
            
            files = []
            total_size = 0
            
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                if file.endswith('.pdf') and os.path.isfile(file_path):
                    files.append(file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (PermissionError, OSError) as e:
                        logger.error(f"Error getting file size for {file}: {str(e)}")
            
            return {
                "cache_dir": self.cache_dir,
                "file_count": len(files),
                "total_size": total_size,
                "files": files,
                "status": "Success"
            }
        except (PermissionError, OSError) as e:
            logger.error(f"Error accessing cache directory: {str(e)}")
            return {
                "error": f"Error accessing cache directory: {str(e)}",
                "cache_dir": self.cache_dir
            }
        except Exception as e:
            logger.error(f"Unexpected error getting cache info: {str(e)}")
            return {
                "error": f"Unexpected error: {str(e)}",
                "cache_dir": self.cache_dir
            }
    
    def get_pdf(self, source: str, timeout: int = 30) -> Optional[str]:
        """
        Get PDF from different sources
        
        Args:
            source: PDF source (local path, URL, or cloud storage path)
            timeout: Request timeout in seconds
            
        Returns:
            Path to PDF file, or None if operation failed
        """
        try:
            # Check if source is a local file
            if os.path.exists(source) and os.path.isfile(source):
                logger.info(f"Using local PDF file: {source}")
                # Check if it's a PDF file
                if source.lower().endswith('.pdf'):
                    return source
                else:
                    logger.warning(f"Local file is not a PDF: {source}")
                    return None
            
            # Check if source is a URL
            elif source.startswith(('http://', 'https://')):
                return self.download(source, timeout)
            
            # Check if source is a cloud storage path (S3, Google Drive, etc.)
            elif source.startswith(('s3://', 'gs://')):
                logger.info(f"Processing cloud storage source: {source}")
                # For now, return None as cloud storage support would require additional dependencies
                # This is a placeholder for future implementation
                logger.warning("Cloud storage support is not yet implemented")
                return None
            
            else:
                logger.error(f"Unknown source type: {source}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing PDF source: {str(e)}")
            return None
