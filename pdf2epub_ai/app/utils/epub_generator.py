from ebooklib import epub
import os
from typing import List, Dict, Any


def generate_epub(chapters: List[tuple], images: Dict[str, bytes], output_path: str, structure: Dict = None):
    """
    Generate EPUB file from formatted chapters and images
    """
    book = epub.EpubBook()
    
    # Set metadata
    if structure and "title" in structure:
        book.set_title(structure["title"])
    else:
        book.set_title("Converted Book")
    
    if structure and "author" in structure:
        book.add_author(structure["author"])
    else:
        book.add_author("Unknown Author")
    
    book.set_identifier("pdf2epub")
    book.set_language("en")
    
    # Add CSS styling
    style = """
    body {
        font-family: serif;
        line-height: 1.6;
        margin-left: 5%;
        margin-right: 5%;
    }
    
    h1.chapter-title {
        text-align: center;
        margin-top: 3em;
        margin-bottom: 2em;
        page-break-before: always;
    }
    
    p.para {
        text-indent: 1.5em;
        margin-top: 0.6em;
    }
    
    p.dialogue {
        margin-left: 1em;
        text-indent: 0;
    }
    
    p.short-line {
        text-align: center;
        font-style: italic;
        text-indent: 0;
    }
    
    p.scene-break {
        text-align: center;
        margin: 2em 0;
    }
    
    blockquote {
        margin-left: 2em;
        font-style: italic;
    }
    """
    
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/style.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)
    
    # Add images
    for img_path, img_data in images.items():
        img_item = epub.EpubItem(
            uid=img_path,
            file_name=f"images/{img_path}",
            media_type="image/png",
            content=img_data
        )
        book.add_item(img_item)
    
    # Create chapters
    epub_chapters = []
    
    for i, (title, content) in enumerate(chapters):
        chapter = epub.EpubHtml(
            title=title,
            file_name=f'chapter_{i}.xhtml',
            lang='en'
        )
        
        chapter_html = f'<h1 class="chapter-title">{title}</h1>\n'
        for p in content:
            chapter_html += p + "\n"
        
        chapter.content = f"""
        <html>
        <head>
        <link href="style/style.css" rel="stylesheet" type="text/css"/>
        </head>
        <body>
        {chapter_html}
        </body>
        </html>
        """
        
        chapter.add_item(nav_css)
        book.add_item(chapter)
        epub_chapters.append(chapter)
    
    # Create table of contents
    book.toc = tuple(epub_chapters)
    
    # Add navigation files
    book.spine = ['nav'] + epub_chapters
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    
    # Write EPUB file
    epub.write_epub(output_path, book)
    print(f"EPUB file generated successfully: {output_path}")