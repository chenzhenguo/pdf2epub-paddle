import os
import zipfile
from typing import Dict, Any, Optional
from app.utils.logger import logger


class EPUBValidator:
    """
    EPUB quality validation class
    """
    def __init__(self):
        """
        Initialize EPUBValidator
        """
        pass
    
    def validate_epub(self, epub_path: str) -> Dict[str, Any]:
        """
        Validate EPUB file
        
        Args:
            epub_path: Path to EPUB file
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "epub_path": epub_path,
            "valid": False,
            "errors": [],
            "warnings": [],
            "metadata": {},
            "structure": {}
        }
        
        try:
            # Check if file exists
            if not os.path.exists(epub_path):
                results["errors"].append("EPUB file does not exist")
                return results
            
            # Check if file is a valid ZIP
            if not self._is_valid_zip(epub_path):
                results["errors"].append("EPUB file is not a valid ZIP archive")
                return results
            
            # Validate EPUB structure
            structure_valid, structure_info = self._validate_structure(epub_path)
            results["structure"] = structure_info
            
            if not structure_valid:
                results["errors"].extend(structure_info.get("errors", []))
            
            # Validate metadata
            metadata_valid, metadata = self._validate_metadata(epub_path)
            results["metadata"] = metadata
            
            if not metadata_valid:
                results["errors"].extend(metadata.get("errors", []))
            
            # Check file size
            file_size = os.path.getsize(epub_path)
            results["file_size"] = file_size
            
            if file_size == 0:
                results["errors"].append("EPUB file is empty")
            elif file_size > 500 * 1024 * 1024:  # 500MB
                results["warnings"].append("EPUB file is very large")
            
            # Determine overall validity
            results["valid"] = len(results["errors"]) == 0
            
            logger.info(f"EPUB validation completed: {epub_path}")
            logger.info(f"Valid: {results['valid']}, Errors: {len(results['errors'])}, Warnings: {len(results['warnings'])}")
            
        except Exception as e:
            error_msg = f"Error during validation: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def _is_valid_zip(self, file_path: str) -> bool:
        """
        Check if file is a valid ZIP archive
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid ZIP
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                return True
        except zipfile.BadZipFile:
            return False
        except Exception:
            return False
    
    def _validate_structure(self, epub_path: str) -> tuple[bool, Dict[str, Any]]:
        """
        Validate EPUB structure
        
        Args:
            epub_path: Path to EPUB file
            
        Returns:
            (is_valid, structure_info)
        """
        structure_info = {
            "has_mimetype": False,
            "has_meta_inf": False,
            "has_content_opf": False,
            "has_nav": False,
            "has_ncx": False,
            "errors": []
        }
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as zf:
                file_list = zf.namelist()
                
                # Check for required files
                if 'mimetype' in file_list:
                    structure_info["has_mimetype"] = True
                else:
                    structure_info["errors"].append("Missing mimetype file")
                
                if 'META-INF/' in file_list or any(f.startswith('META-INF/') for f in file_list):
                    structure_info["has_meta_inf"] = True
                else:
                    structure_info["errors"].append("Missing META-INF directory")
                
                # Check for content.opf
                content_opf_files = [f for f in file_list if f.endswith('content.opf')]
                if content_opf_files:
                    structure_info["has_content_opf"] = True
                else:
                    structure_info["errors"].append("Missing content.opf file")
                
                # Check for navigation files
                nav_files = [f for f in file_list if f.endswith('nav.xhtml') or f.endswith('nav.html')]
                if nav_files:
                    structure_info["has_nav"] = True
                else:
                    structure_info["warnings"] = structure_info.get("warnings", [])
                    structure_info["warnings"].append("Missing navigation file (nav.xhtml)")
                
                # Check for NCX file
                ncx_files = [f for f in file_list if f.endswith('.ncx')]
                if ncx_files:
                    structure_info["has_ncx"] = True
                else:
                    structure_info["warnings"] = structure_info.get("warnings", [])
                    structure_info["warnings"].append("Missing NCX file")
                
                # Check mimetype content
                if 'mimetype' in file_list:
                    with zf.open('mimetype') as f:
                        content = f.read().decode('utf-8').strip()
                        if content != 'application/epub+zip':
                            structure_info["errors"].append(f"Invalid mimetype: {content}")
        
        except Exception as e:
            structure_info["errors"].append(f"Error validating structure: {str(e)}")
        
        is_valid = len(structure_info["errors"]) == 0
        return is_valid, structure_info
    
    def _validate_metadata(self, epub_path: str) -> tuple[bool, Dict[str, Any]]:
        """
        Validate EPUB metadata
        
        Args:
            epub_path: Path to EPUB file
            
        Returns:
            (is_valid, metadata)
        """
        metadata = {
            "title": None,
            "author": None,
            "language": None,
            "identifier": None,
            "errors": []
        }
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as zf:
                # Find content.opf file
                content_opf_files = [f for f in zf.namelist() if f.endswith('content.opf')]
                
                if not content_opf_files:
                    metadata["errors"].append("content.opf not found")
                    return False, metadata
                
                # Read content.opf
                content_opf_path = content_opf_files[0]
                with zf.open(content_opf_path) as f:
                    content = f.read().decode('utf-8')
                
                # Extract basic metadata
                import re
                
                # Title
                title_match = re.search(r'<dc:title>(.*?)</dc:title>', content, re.DOTALL)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()
                else:
                    metadata["errors"].append("Title not found")
                
                # Author
                author_match = re.search(r'<dc:creator.*?>(.*?)</dc:creator>', content, re.DOTALL)
                if author_match:
                    metadata["author"] = author_match.group(1).strip()
                else:
                    metadata["warnings"] = metadata.get("warnings", [])
                    metadata["warnings"].append("Author not found")
                
                # Language
                language_match = re.search(r'<dc:language>(.*?)</dc:language>', content, re.DOTALL)
                if language_match:
                    metadata["language"] = language_match.group(1).strip()
                else:
                    metadata["warnings"] = metadata.get("warnings", [])
                    metadata["warnings"].append("Language not found")
                
                # Identifier
                identifier_match = re.search(r'<dc:identifier.*?>(.*?)</dc:identifier>', content, re.DOTALL)
                if identifier_match:
                    metadata["identifier"] = identifier_match.group(1).strip()
                else:
                    metadata["warnings"] = metadata.get("warnings", [])
                    metadata["warnings"].append("Identifier not found")
        
        except Exception as e:
            metadata["errors"].append(f"Error validating metadata: {str(e)}")
        
        is_valid = len(metadata["errors"]) == 0
        return is_valid, metadata
    
    def validate_epub_visual(self, epub_path: str) -> Dict[str, Any]:
        """
        Perform visual validation of EPUB
        
        Args:
            epub_path: Path to EPUB file
            
        Returns:
            Dictionary with visual validation results
        """
        visual_results = {
            "epub_path": epub_path,
            "has_chapters": False,
            "chapter_count": 0,
            "has_images": False,
            "image_count": 0,
            "warnings": []
        }
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as zf:
                file_list = zf.namelist()
                
                # Count chapters (HTML/XHTML files)
                chapter_files = [f for f in file_list if f.endswith('.html') or f.endswith('.xhtml')]
                visual_results["chapter_count"] = len(chapter_files)
                visual_results["has_chapters"] = len(chapter_files) > 0
                
                if len(chapter_files) == 0:
                    visual_results["warnings"].append("No chapter files found")
                
                # Count images
                image_files = [f for f in file_list if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                visual_results["image_count"] = len(image_files)
                visual_results["has_images"] = len(image_files) > 0
                
                # Check for CSS files
                css_files = [f for f in file_list if f.endswith('.css')]
                if len(css_files) == 0:
                    visual_results["warnings"].append("No CSS files found")
                
        except Exception as e:
            visual_results["warnings"].append(f"Error during visual validation: {str(e)}")
        
        return visual_results
    
    def get_epub_info(self, epub_path: str) -> Optional[Dict[str, Any]]:
        """
        Get EPUB information
        
        Args:
            epub_path: Path to EPUB file
            
        Returns:
            Dictionary with EPUB info or None if error
        """
        try:
            validation_results = self.validate_epub(epub_path)
            visual_results = self.validate_epub_visual(epub_path)
            
            return {
                **validation_results,
                **visual_results,
                "combined_valid": validation_results.get("valid", False)
            }
        except Exception as e:
            logger.error(f"Error getting EPUB info: {str(e)}")
            return None
