import os
import re
from typing import Dict, List, Optional, Tuple
from ebooklib import epub
from lxml import etree
from PIL import Image
import requests

class EPUBValidator:
    """Comprehensive EPUB validator with structural, visual, and metadata validation"""
    
    def __init__(self, epub_path: str):
        """Initialize validator with EPUB file path"""
        self.epub_path = epub_path
        self.book = None
        self.errors = []
        self.warnings = []
    
    def validate_structure(self) -> Tuple[bool, List[str], List[str]]:
        """Validate EPUB structural integrity using ebooklib"""
        try:
            self.book = epub.read_epub(self.epub_path)
            
            # Check for required EPUB components
            self._check_required_components()
            
            # Validate OPF structure
            self._validate_opf_structure()
            
            # Check for broken internal links
            self._check_internal_links()
            
            # Validate navigation structure
            self._validate_navigation()
            
            return len(self.errors) == 0, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Failed to open EPUB: {str(e)}")
            return False, self.errors, self.warnings
    
    def _check_required_components(self):
        """Check for required EPUB components"""
        # Check for navigation file
        nav_items = [item for item in self.book.get_items() if hasattr(item, 'get_name') and ('nav' in item.get_name().lower() or isinstance(item, epub.EpubNav))]
        if not nav_items:
            # Check for NCX file as alternative navigation
            ncx_items = [item for item in self.book.get_items() if hasattr(item, 'get_name') and 'ncx' in item.get_name().lower()]
            if not ncx_items:
                self.errors.append("No navigation file found")
        
        # Check for at least one content file
        content_items = [item for item in self.book.get_items() if hasattr(item, 'get_name') and any(ext in item.get_name().lower() for ext in ['.html', '.xhtml', '.css', '.jpg', '.jpeg', '.png', '.gif'])]
        if not content_items:
            self.errors.append("No content files found")
    
    def _validate_opf_structure(self):
        """Validate OPF structure using ebooklib API"""
        try:
            # Check for required metadata fields using ebooklib API
            title = self.book.get_metadata('DC', 'title')
            if not title or not title[0][0]:
                self.errors.append("Missing or empty title in metadata")
            
            creator = self.book.get_metadata('DC', 'creator')
            if not creator or not creator[0][0]:
                self.warnings.append("Missing or empty creator in metadata")
        except Exception as e:
            self.errors.append(f"Error validating metadata: {str(e)}")
    
    def _check_internal_links(self):
        """Check for broken internal links"""
        for item in self.book.get_items():
            if hasattr(item, 'get_name') and any(ext in item.get_name().lower() for ext in ['.html', '.xhtml']):
                try:
                    content = item.get_content().decode('utf-8')
                    # Find all internal links
                    internal_links = re.findall(r'href=["\']([^"\']+)["\']', content)
                    for link in internal_links:
                        # Skip external links
                        if link.startswith(('http://', 'https://', 'mailto:')):
                            continue
                        # Check if the linked item exists
                        found = False
                        for other_item in self.book.get_items():
                            if hasattr(other_item, 'get_name') and other_item.get_name() == link:
                                found = True
                                break
                        if not found:
                            self.warnings.append(f"Broken internal link: {link} in {item.get_name()}")
                except Exception as e:
                    self.warnings.append(f"Error checking links in {item.get_name()}: {str(e)}")
    
    def _validate_navigation(self):
        """Validate navigation structure"""
        nav_items = [item for item in self.book.get_items() if hasattr(item, 'get_name') and ('nav' in item.get_name().lower() or isinstance(item, epub.EpubNav))]
        if not nav_items:
            return
        
        try:
            nav_content = nav_items[0].get_content().decode('utf-8')
            root = etree.fromstring(nav_content.encode('utf-8'))
            
            # Check for navigation elements
            nav_points = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if not nav_points:
                # Check for NCX format
                nav_points = root.findall('.//{http://www.daisy.org/z3986/2005/ncx/}navPoint')
                if not nav_points:
                    # Check for other navigation formats
                    if 'nav' in nav_content.lower() and 'href' in nav_content.lower():
                        # This is likely a valid navigation file with a different format
                        pass
                    else:
                        self.warnings.append("No navigation points found")
        except Exception as e:
            self.errors.append(f"Invalid navigation structure: {str(e)}")
    
    def validate_visual(self) -> Tuple[bool, List[str], List[str]]:
        """Validate visual elements of EPUB"""
        if not self.book:
            try:
                self.book = epub.read_epub(self.epub_path)
            except Exception as e:
                self.errors.append(f"Failed to open EPUB: {str(e)}")
                return False, self.errors, self.warnings
        
        # Check images
        self._validate_images()
        
        # Check for accessibility
        self._check_accessibility()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_images(self):
        """Validate images in EPUB"""
        for item in self.book.get_items():
            if hasattr(item, 'get_name') and any(ext in item.get_name().lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                try:
                    # Try to open image to check validity
                    image_data = item.get_content()
                    img = Image.open(image_data)
                    img.verify()
                    
                    # Check image dimensions and size
                    img = Image.open(image_data)
                    width, height = img.size
                    if width > 4000 or height > 4000:
                        self.warnings.append(f"Large image detected: {item.get_name()} ({width}x{height})")
                    
                    # Check file size
                    if len(image_data) > 10 * 1024 * 1024:  # 10MB
                        self.warnings.append(f"Large image file: {item.get_name()} ({len(image_data)/1024/1024:.2f}MB)")
                except Exception as e:
                    self.errors.append(f"Invalid image: {item.get_name()}: {str(e)}")
    
    def _check_accessibility(self):
        """Check accessibility features"""
        for item in self.book.get_items():
            if hasattr(item, 'get_name') and any(ext in item.get_name().lower() for ext in ['.html', '.xhtml']):
                try:
                    content = item.get_content().decode('utf-8')
                    
                    # Check for alt text on images
                    if '<img' in content and 'alt=' not in content:
                        self.warnings.append(f"Missing alt text for images in {item.get_name()}")
                    
                    # Check for proper heading structure
                    headings = re.findall(r'<h[1-6]', content)
                    if not headings:
                        self.warnings.append(f"No heading structure found in {item.get_name()}")
                except Exception as e:
                    self.warnings.append(f"Error checking accessibility in {item.get_name()}: {str(e)}")
    
    def validate_metadata(self) -> Tuple[bool, List[str], List[str]]:
        """Validate EPUB metadata"""
        if not self.book:
            try:
                self.book = epub.read_epub(self.epub_path)
            except Exception as e:
                self.errors.append(f"Failed to open EPUB: {str(e)}")
                return False, self.errors, self.warnings
        
        # Check metadata completeness
        self._check_metadata_completeness()
        
        # Check metadata validity
        self._check_metadata_validity()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_metadata_completeness(self):
        """Check metadata completeness using ebooklib API"""
        try:
            # Check for recommended metadata fields using ebooklib API
            required_fields = [
                ('title', 'title'),
                ('creator', 'creator'),
                ('language', 'language'),
                ('publisher', 'publisher'),
                ('date', 'date')
            ]
            
            for field_name, field_key in required_fields:
                field = self.book.get_metadata('DC', field_key)
                if not field or not field[0][0]:
                    self.warnings.append(f"Missing or empty {field_name} in metadata")
        except Exception as e:
            self.errors.append(f"Error checking metadata completeness: {str(e)}")
    
    def _check_metadata_validity(self):
        """Check metadata validity using ebooklib API"""
        try:
            # Check language code format
            language = self.book.get_metadata('DC', 'language')
            if language and language[0][0]:
                # Basic check for language code format
                if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', language[0][0]):
                    self.warnings.append(f"Invalid language code format: {language[0][0]}")
            
            # Check date format
            date = self.book.get_metadata('DC', 'date')
            if date and date[0][0]:
                # Basic check for ISO 8601 date format
                if not re.match(r'^\d{4}(-\d{2}(-\d{2})?)?$', date[0][0]):
                    self.warnings.append(f"Invalid date format: {date[0][0]}. Should be ISO 8601 format (YYYY-MM-DD)")
        except Exception as e:
            self.errors.append(f"Error checking metadata validity: {str(e)}")
    
    def validate_all(self) -> Dict[str, Tuple[bool, List[str], List[str]]]:
        """Run all validation checks"""
        results = {
            'structure': self.validate_structure(),
            'visual': self.validate_visual(),
            'metadata': self.validate_metadata()
        }
        return results

    def get_summary(self) -> str:
        """Get validation summary"""
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        summary = f"EPUB Validation Summary for {self.epub_path}\n"
        summary += f"Total errors: {total_errors}\n"
        summary += f"Total warnings: {total_warnings}\n"
        
        if self.errors:
            summary += "\nErrors:\n"
            for error in self.errors:
                summary += f"- {error}\n"
        
        if self.warnings:
            summary += "\nWarnings:\n"
            for warning in self.warnings:
                summary += f"- {warning}\n"
        
        return summary