import os
import tempfile
import pytest
from src.epub_validator import EPUBValidator
from ebooklib import epub

def create_test_epub(filename):
    """Create a simple test EPUB file"""
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier('id12345')
    book.set_title('Test EPUB')
    book.set_language('en')
    book.add_author('Test Author')
    book.add_metadata('DC', 'publisher', 'Test Publisher')
    book.add_metadata('DC', 'date', '2023-01-01')
    
    # Create chapter
    c1 = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
    c1.content = '''<html><body><h1>Chapter 1</h1><p>Test content</p></body></html>'''
    
    # Create navigation
    book.add_item(c1)
    book.toc = (epub.Link('chap_01.xhtml', 'Chapter 1', 'chap1'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define spine
    book.spine = ['nav', c1]
    
    # Write EPUB
    epub.write_epub(filename, book, {})

def create_invalid_epub(filename):
    """Create an invalid EPUB file (missing required components)"""
    # Create a minimal invalid EPUB
    with open(filename, 'w') as f:
        f.write('This is not a valid EPUB')

def test_valid_epub():
    """Test validation of a valid EPUB"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_test_epub(tmp_filename)
        validator = EPUBValidator(tmp_filename)
        results = validator.validate_all()
        
        # Check that all validations pass
        assert results['structure'][0] == True
        assert results['visual'][0] == True
        assert results['metadata'][0] == True
        
        # Check that no errors are reported
        assert len(results['structure'][1]) == 0
        assert len(results['visual'][1]) == 0
        assert len(results['metadata'][1]) == 0
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

def test_invalid_epub():
    """Test validation of an invalid EPUB"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_invalid_epub(tmp_filename)
        validator = EPUBValidator(tmp_filename)
        results = validator.validate_all()
        
        # Check that structure validation fails
        assert results['structure'][0] == False
        assert len(results['structure'][1]) > 0
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

def test_metadata_validation():
    """Test metadata validation specifically"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_test_epub(tmp_filename)
        validator = EPUBValidator(tmp_filename)
        valid, errors, warnings = validator.validate_metadata()
        
        # Check that metadata validation passes
        assert valid == True
        assert len(errors) == 0
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

def test_visual_validation():
    """Test visual validation specifically"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_test_epub(tmp_filename)
        validator = EPUBValidator(tmp_filename)
        valid, errors, warnings = validator.validate_visual()
        
        # Check that visual validation passes
        assert valid == True
        assert len(errors) == 0
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

def test_structure_validation():
    """Test structure validation specifically"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_test_epub(tmp_filename)
        validator = EPUBValidator(tmp_filename)
        valid, errors, warnings = validator.validate_structure()
        
        # Check that structure validation passes
        assert valid == True
        assert len(errors) == 0
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

def test_summary():
    """Test summary generation"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_test_epub(tmp_filename)
        validator = EPUBValidator(tmp_filename)
        validator.validate_all()
        summary = validator.get_summary()
        
        # Check that summary contains expected information
        assert 'EPUB Validation Summary' in summary
        assert 'Total errors: 0' in summary
        assert 'Total warnings: 0' in summary
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

if __name__ == '__main__':
    pytest.main(['-v', __file__])