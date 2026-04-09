import uuid
from app.utils.test_case_manager import TestCase, TestCaseManager
from app.utils.logger import logger


def generate_test_cases():
    """
    Generate comprehensive test cases
    """
    manager = TestCaseManager()
    
    # Clear existing test cases to avoid duplicates
    existing_cases = manager.list_test_cases()
    for case in existing_cases:
        manager.delete_test_case(case.test_id)
    
    # Test cases for different PDF types
    online_test_cases = [
        # Books
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="Alice's Adventures in Wonderland",
            description="Classic book by Lewis Carroll",
            pdf_source="https://www.gutenberg.org/files/11/11-pdf.pdf",
            is_online=True,
            expected_title="Alice's Adventures in Wonderland",
            expected_author="Lewis Carroll",
            tags=["online", "book", "classic", "text-heavy"]
        ),
        # Academic articles
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="Attention Is All You Need",
            description="Seminal research paper on transformers",
            pdf_source="https://arxiv.org/pdf/1706.03762.pdf",
            is_online=True,
            expected_title="Attention Is All You Need",
            tags=["online", "article", "academic", "technical"]
        ),
        # Reports
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="Global Trends Report",
            description="World Economic Forum global trends report",
            pdf_source="https://www.weforum.org/reports/global-trends-report-2023",
            is_online=True,
            expected_title="Global Trends Report",
            tags=["online", "report", "business", "structured"]
        ),
        # Scientific papers
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="COVID-19 Research Paper",
            description="Scientific research on COVID-19",
            pdf_source="https://www.nature.com/articles/s41586-020-2012-7.pdf",
            is_online=True,
            expected_title="A pneumonia outbreak associated with a new coronavirus of probable bat origin",
            tags=["online", "article", "scientific", "technical"]
        ),
        # Technical documentation
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="Python Documentation",
            description="Python programming language documentation",
            pdf_source="https://docs.python.org/3/pdf/python-3.10.0-docs-pdf.pdf",
            is_online=True,
            expected_title="Python Documentation",
            tags=["online", "documentation", "technical", "structured"]
        ),
        # Brochures
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="Sample Brochure",
            description="Marketing brochure with images and text",
            pdf_source="https://www.adobe.com/content/dam/acom/en/products/document-cloud/pdf-services/pdf-packaging-brochure.pdf",
            is_online=True,
            expected_title="PDF Packaging",
            tags=["online", "brochure", "marketing", "images"]
        )
    ]
    
    # Edge cases
    edge_case_test_cases = [
        # Empty PDF
        TestCase(
            test_id=f"edge_{uuid.uuid4()}",
            name="Empty PDF",
            description="Completely empty PDF file",
            pdf_source="https://www.dropbox.com/s/7k1b7c2a3d4e5f6/empty.pdf?dl=1",
            is_online=True,
            expected_title="Empty PDF",
            tags=["online", "edge", "empty"]
        ),
        # Very small PDF
        TestCase(
            test_id=f"edge_{uuid.uuid4()}",
            name="Small PDF",
            description="Very small PDF with minimal content",
            pdf_source="https://www.dropbox.com/s/1a2b3c4d5e6f7g8/small.pdf?dl=1",
            is_online=True,
            expected_title="Small PDF",
            tags=["online", "edge", "small"]
        ),
        # PDF with only images
        TestCase(
            test_id=f"edge_{uuid.uuid4()}",
            name="Image-only PDF",
            description="PDF containing only images, no text",
            pdf_source="https://www.dropbox.com/s/9h8g7f6e5d4c3b2/image_only.pdf?dl=1",
            is_online=True,
            expected_title="Image-only PDF",
            tags=["online", "edge", "images"]
        ),
        # PDF with complex formatting
        TestCase(
            test_id=f"edge_{uuid.uuid4()}",
            name="Complex Formatting PDF",
            description="PDF with complex layouts and formatting",
            pdf_source="https://www.dropbox.com/s/5t6u7v8w9x0y1z2/complex_formatting.pdf?dl=1",
            is_online=True,
            expected_title="Complex Formatting PDF",
            tags=["online", "edge", "complex"]
        )
    ]
    
    # Different conversion scenarios
    conversion_test_cases = [
        # PDF with tables
        TestCase(
            test_id=f"conversion_{uuid.uuid4()}",
            name="PDF with Tables",
            description="PDF containing tables that need proper conversion",
            pdf_source="https://www.dropbox.com/s/3a4b5c6d7e8f9g0/tables.pdf?dl=1",
            is_online=True,
            expected_title="PDF with Tables",
            tags=["online", "conversion", "tables"]
        ),
        # PDF with footnotes
        TestCase(
            test_id=f"conversion_{uuid.uuid4()}",
            name="PDF with Footnotes",
            description="PDF containing footnotes and endnotes",
            pdf_source="https://www.dropbox.com/s/2p3q4r5s6t7u8v9/footnotes.pdf?dl=1",
            is_online=True,
            expected_title="PDF with Footnotes",
            tags=["online", "conversion", "footnotes"]
        ),
        # PDF with multiple columns
        TestCase(
            test_id=f"conversion_{uuid.uuid4()}",
            name="Multi-column PDF",
            description="PDF with multiple columns of text",
            pdf_source="https://www.dropbox.com/s/7x8y9z0a1b2c3d4/multicolumn.pdf?dl=1",
            is_online=True,
            expected_title="Multi-column PDF",
            tags=["online", "conversion", "columns"]
        ),
        # Scanned PDF (OCR required)
        TestCase(
            test_id=f"conversion_{uuid.uuid4()}",
            name="Scanned PDF",
            description="Scanned PDF that requires OCR",
            pdf_source="https://www.dropbox.com/s/5f6g7h8i9j0k1l2/scanned.pdf?dl=1",
            is_online=True,
            expected_title="Scanned PDF",
            tags=["online", "conversion", "ocr"]
        )
    ]
    
    # Combine all test cases
    all_test_cases = online_test_cases + edge_case_test_cases + conversion_test_cases
    
    # Save test cases
    for test_case in all_test_cases:
        success = manager.save_test_case(test_case)
        if success:
            logger.info(f"Test case saved: {test_case.name}")
        else:
            logger.error(f"Failed to save test case: {test_case.name}")
    
    logger.info(f"Generated {len(all_test_cases)} test cases")
    return all_test_cases


if __name__ == "__main__":
    generate_test_cases()
