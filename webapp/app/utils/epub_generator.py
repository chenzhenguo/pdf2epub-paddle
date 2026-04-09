import os
import re
from ebooklib import epub


def create_epub(title: str, results: list, output_file: str, image_dir: str,
                cover_image_path: str = None, author: str = None,
                confirmed_headings: list = None):
    """
    Creates an EPUB file from the aggregated API results.
    """
    book = epub.EpubBook()
    book.set_identifier(f"id_{title}")
    book.set_title(title)
    book.set_language("en")  # Or auto-detect?

    if author:
        book.add_author(author)

    # Set cover image
    if cover_image_path and os.path.exists(cover_image_path):
        with open(cover_image_path, "rb") as f:
            cover_data = f.read()
        book.set_cover("cover.png", cover_data)

    chapters = []

    # CSS for the book
    style = """
    body { font-family: serif; line-height: 1.8; text-align: justify; margin: 1em; }
    h1 { text-align: center; margin: 1.5em 0 0.8em 0; font-size: 1.6em; }
    h2 { margin: 1.2em 0 0.6em 0; font-size: 1.3em; }
    h3 { margin: 1em 0 0.5em 0; font-size: 1.1em; }
    p { margin-bottom: 0.8em; }
    blockquote { margin: 1em 2em; font-style: italic; }
    img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
    """
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style
    )
    book.add_item(nav_css)

    # Process each chunk's result
    full_markdown = ""

    for chunk_idx, result in enumerate(results):
        if not result or "result" not in result:
            continue

        layout_results = result["result"].get("layoutParsingResults", [])

        for i, page_res in enumerate(layout_results):
            # 1. Get Markdown Text
            page_md = page_res["markdown"]["text"]

            # 2. Handle Images
            images_map = page_res["markdown"].get("images", {})

            for rel_path, img_url in images_map.items():
                # Define local path where we downloaded the image
                local_img_path = os.path.join(image_dir, rel_path)

                # Check if we successfully downloaded it
                if os.path.exists(local_img_path):
                    # Add to EPUB
                    # Read image data
                    with open(local_img_path, "rb") as img_f:
                        img_data = img_f.read()

                    # Create EPUB Image Item
                    epub_img = epub.EpubImage()
                    epub_img.file_name = rel_path
                    epub_img.media_type = (
                        "image/jpeg"  # Assuming JPG, might need detection
                    )
                    epub_img.content = img_data

                    if rel_path not in [item.file_name for item in book.get_items()]:
                        book.add_item(epub_img)

            # 3. Concatenate Text with paragraph reflow
            lines = page_md.split("\n")
            cleaned_lines = []
            for line in lines:
                # Basic Page Number Removal (digit only)
                if line.strip().isdigit():
                    continue
                cleaned_lines.append(line)
            
            # Reflow: join lines that appear to be part of the same paragraph
            reflowed_paragraphs = []
            current_para = ""
            
            # Terminal punctuation that indicates end of sentence/paragraph
            terminal_chars = ('.', '!', '?', '"', "'", ')', ']', '}', ':', ';')
            # Patterns that indicate a line is a header or special block
            header_pattern = re.compile(r'^(#{1,6}\s|>|\s*[-*]\s|\d+\.)')
            # Characters that indicate a line should not be joined with next
            non_join_endings = (':', ';', ',', '-')
            
            for i, line in enumerate(cleaned_lines):
                stripped = line.rstrip()
                if not stripped:
                    # Empty line indicates paragraph break
                    if current_para:
                        reflowed_paragraphs.append(current_para)
                        current_para = ""
                    continue
                
                # Check if this line is a header/list/blockquote
                is_special = header_pattern.match(stripped)
                
                if is_special:
                    # Flush current paragraph before special line
                    if current_para:
                        reflowed_paragraphs.append(current_para)
                        current_para = ""
                    reflowed_paragraphs.append(stripped)
                elif not current_para:
                    # Start of new paragraph
                    current_para = stripped
                else:
                    # Check if current_para ends with terminal punctuation
                    # or if it ends with colon/comma/semicolon (likely list/address item)
                    current_ends = current_para.rstrip()
                    
                    if current_ends.endswith(terminal_chars):
                        # Previous paragraph ends with terminal punctuation
                        # This line starts a new paragraph
                        reflowed_paragraphs.append(current_para)
                        current_para = stripped
                    elif current_ends and current_ends[-1] in non_join_endings:
                        # Previous line ends with :, ;, , or - - likely list item or address
                        # Don't join, start new paragraph
                        reflowed_paragraphs.append(current_para)
                        current_para = stripped
                    elif len(stripped) < 20 and not stripped.endswith(terminal_chars):
                        # Short line that doesn't end with punctuation - might be 
                        # a title, caption, or deliberate short line (poetry, etc.)
                        reflowed_paragraphs.append(current_para)
                        current_para = stripped
                    else:
                        # Likely continuation of same paragraph
                        current_para = current_ends + " " + stripped
            
            # Don't forget the last paragraph
            if current_para:
                reflowed_paragraphs.append(current_para)
            
            # Join paragraphs and append to full_markdown
            page_markdown = "\n\n".join(reflowed_paragraphs)
            
            if full_markdown and page_markdown:
                # Check if full_markdown ends mid-sentence (no terminal punctuation)
                # and page_markdown starts with a continuation (not a header)
                full_stripped = full_markdown.rstrip()
                page_lines = page_markdown.split('\n')
                first_page_line = page_lines[0].strip() if page_lines else ""
                
                # Check if we should merge (previous doesn't end with terminal, next isn't a header)
                ends_mid_sentence = full_stripped and not full_stripped.endswith(terminal_chars)
                next_is_header = header_pattern.match(first_page_line) if first_page_line else False
                
                if ends_mid_sentence and not next_is_header:
                    # Merge: remove the trailing newlines and join with space
                    full_markdown = full_markdown.rstrip() + " " + page_markdown + "\n\n"
                else:
                    full_markdown += page_markdown + "\n\n"
            else:
                full_markdown += page_markdown + "\n\n"

    # Split markdown into chapters based on headers (# Header)
    md_lines = full_markdown.split("\n")
    current_chapter_title = "Start"
    current_chapter_content = []
    chapter_count = 0

    # Regex to identify "Major" headers (Chapters/Parts) to split on (legacy fallback)
    major_header_pattern = re.compile(
        r"^(#{1,2})\s+(?:Chapter|Part|Lecture|Preface|Intro|Appendix|Prologue|Epilogue|Conclusion|Book|Acknowledgements|Contents|Abstract|序|前言|导论|目录|第[零一二三四五六七八九十百千0-9]+[篇章讲]).*"
    )

    # Regex for ANY header to format as H1/H2 in HTML but not necessarily split
    any_header_pattern = re.compile(r"^(#{1,2})\s+(.+)$")

    # Build set of confirmed heading titles for O(1) lookup
    if confirmed_headings is not None:
        confirmed_titles = {h["title"] for h in confirmed_headings}
    else:
        confirmed_titles = None  # use legacy regex fallback

    for line in md_lines:
        # Check if line is a header (before LaTeX cleanup, to match extracted candidates)
        match = any_header_pattern.match(line)
        is_split_point = False
        if match:
            heading_text = match.group(2).strip()
            # Clean LaTeX artifacts for matching
            heading_text = re.sub(r"\$\s*\\underline\{(.+?)\}\s*\$", "", heading_text).strip()
            heading_text = re.sub(r"^\d+\s+", "", heading_text).strip()
            # Determine if this heading is a chapter split point
            if confirmed_titles is not None:
                is_split_point = heading_text in confirmed_titles
            else:
                is_split_point = bool(major_header_pattern.match(line))

        # Clean up LaTeX artifacts
        line = re.sub(r"\$\s*\^\{(.+?)\}\s*\$", r"", line)  # superscripts
        line = re.sub(r"\$\s*\\underline\{(.+?)\}\s*\$", "", line)  # underlines

        if match:
            if is_split_point:
                # If we have content for the previous chapter, save it
                if current_chapter_content:
                    # Determine filename
                    safe_title = "".join(
                        [
                            c
                            for c in current_chapter_title
                            if c.isalnum() or c in (" ", "_", "-")
                        ]
                    ).strip()
                    if not safe_title:
                        safe_title = f"chap_{chapter_count}"

                    c = epub.EpubHtml(
                        title=current_chapter_title,
                        file_name=f"{safe_title}_{chapter_count}.xhtml",
                        lang="en",
                    )

                    try:
                        import markdown

                        html_content = markdown.markdown(
                            "\n".join(current_chapter_content)
                        )
                    except ImportError:
                        html_content = (
                            "<p>" + "</p><p>".join(current_chapter_content) + "</p>"
                        )

                    c.content = f"<html><head><link rel='stylesheet' href='style/nav.css'/></head><body>{html_content}</body></html>"
                    c.add_item(nav_css)
                    book.add_item(c)
                    chapters.append(c)
                    chapter_count += 1

                current_chapter_title = match.group(2)
                current_chapter_content = [line]
            else:
                # It's a minor header (e.g. Section), just keep it in flow
                current_chapter_content.append(line)
        else:
            current_chapter_content.append(line)

    # Add last chapter
    if current_chapter_content:
        # Determine filename
        safe_title = "".join(
            [c for c in current_chapter_title if c.isalnum() or c in (" ", "_", "-")]
        ).strip()
        if not safe_title:
            safe_title = f"chap_{chapter_count}"

        c = epub.EpubHtml(
            title=current_chapter_title,
            file_name=f"{safe_title}_{chapter_count}.xhtml",
            lang="en",
        )
        try:
            import markdown

            html_content = markdown.markdown("\n".join(current_chapter_content))
        except ImportError:
            html_content = "<p>" + "</p><p>".join(current_chapter_content) + "</p>"

        c.content = f"<html><head><link rel='stylesheet' href='style/nav.css'/></head><body>{html_content}</body></html>"
        c.add_item(nav_css)
        book.add_item(c)
        chapters.append(c)

    # If no chapters were created (no headers found), create one big chapter
    if not chapters and full_markdown:
        c = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="en")
        try:
            import markdown

            html_content = markdown.markdown(full_markdown)
        except ImportError:
            html_content = "<p>" + "</p><p>".join(full_markdown.split("\n")) + "</p>"
        c.content = f"<html><head><link rel='stylesheet' href='style/nav.css'/></head><body>{html_content}</body></html>"
        book.add_item(c)
        chapters.append(c)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    epub.write_epub(output_file, book, {})
    print(f"[*] EPUB saved to {output_file}")


def generate_epub(chapters, images, output_file):
    """
    Simple EPUB generator for testing purposes
    """
    book = epub.EpubBook()
    book.set_identifier("test_book")
    book.set_title("Test Book")
    book.set_language("en")
    book.add_author("Test Author")

    # Add chapters
    epub_chapters = []
    for i, (title, content) in enumerate(chapters):
        c = epub.EpubHtml(title=title, file_name=f"chapter_{i}.xhtml", lang="en")
        c.content = f"<html><body><h1>{title}</h1><p>{'</p><p>'.join(content)}</p></body></html>"
        book.add_item(c)
        epub_chapters.append(c)

    # Add images
    for img_path, img_data in images.items():
        img = epub.EpubImage()
        img.file_name = os.path.basename(img_path)
        img.content = img_data
        book.add_item(img)

    # Set TOC and spine
    book.toc = tuple(epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_chapters

    # Write EPUB file
    epub.write_epub(output_file, book, {})
