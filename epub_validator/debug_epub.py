#!/usr/bin/env python3
"""
Debug script to inspect the structure of an EPUB file
"""

import tempfile
import os
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

def inspect_epub(filename):
    """Inspect the structure of an EPUB file"""
    print(f"Inspecting EPUB: {filename}")
    print("=" * 60)
    
    try:
        book = epub.read_epub(filename)
        print(f"Book title: {book.get_metadata('DC', 'title')[0][0]}")
        print()
        print("Items:")
        print("-" * 60)
        
        items = list(book.get_items())
        print(f"Number of items: {len(items)}")
        print()
        
        for i, item in enumerate(items):
            print(f"Item {i+1}:")
            print(f"  Name: {item.get_name() if hasattr(item, 'get_name') else 'N/A'}")
            print(f"  ID: {item.get_id() if hasattr(item, 'get_id') else 'N/A'}")
            print(f"  Media type: {item.get_media_type() if hasattr(item, 'get_media_type') else 'N/A'}")
            print(f"  Content length: {len(item.get_content()) if hasattr(item, 'get_content') else 'N/A'}")
            print(f"  Type: {type(item).__name__}")
            print()
            
            # Check if this is an OPF file
            if hasattr(item, 'get_content'):
                try:
                    content = item.get_content().decode('utf-8')
                    if '<package' in content:
                        print("  This appears to be an OPF file!")
                        print()
                except Exception as e:
                    print(f"  Error reading content: {e}")
                    print()
                    
    except Exception as e:
        print(f"Error inspecting EPUB: {e}")

if __name__ == "__main__":
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        tmp_filename = tmp.name
    
    try:
        create_test_epub(tmp_filename)
        inspect_epub(tmp_filename)
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)