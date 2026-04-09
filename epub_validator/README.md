# EPUB Validator

A comprehensive EPUB quality validation module that performs structural, visual, and metadata validation using `ebooklib`, `lxml`, and `Pillow`.

## Features

- **Structural Validation**: Validates EPUB structure using `ebooklib`, checking for required components, valid OPF structure, internal links, and navigation structure.
- **Visual Validation**: Checks images for validity, size, and dimensions, and performs basic accessibility checks.
- **Metadata Validation**: Verifies metadata completeness and validity, including required fields and format checks.
- **Comprehensive Reports**: Generates detailed validation reports with errors and warnings.

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd epub_validator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src.epub_validator import EPUBValidator

# Create validator instance
validator = EPUBValidator('path/to/book.epub')

# Run all validation checks
results = validator.validate_all()

# Get summary
print(validator.get_summary())
```

### Command Line Usage

```bash
python examples/usage_example.py path/to/book.epub
```

## Validation Checks

### Structural Validation
- Presence of required EPUB components (OPF, navigation, content files)
- Valid OPF structure and required metadata elements
- Broken internal links
- Navigation structure validation

### Visual Validation
- Image validity and integrity
- Image size and dimension checks
- Accessibility features (alt text, heading structure)

### Metadata Validation
- Completeness of required metadata fields
- Validity of metadata formats (language codes, dates)

## Testing

Run the test suite to ensure the validator works correctly:

```bash
cd epub_validator
python -m pytest tests/test_epub_validator.py -v
```

## Dependencies

- `ebooklib==0.18` - For EPUB structural validation
- `lxml==4.9.3` - For XML parsing and validation
- `pillow==10.1.0` - For image validation
- `requests==2.31.0` - For potential future network checks
- `pytest==7.4.3` - For testing

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.