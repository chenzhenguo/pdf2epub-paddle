# PDF to EPUB with AI Integration

A comprehensive PDF to EPUB converter that combines advanced PDF text extraction with AI-powered text formatting and structure detection.

## Features

- **Unified Document Extraction**: Uses PyMuPDF for efficient PDF text extraction
- **AI-Powered Structure Detection**: Leverages LLM models to detect book structure, including chapters and sections
- **Intelligent Text Formatting**: Uses LLM models to format text for better readability
- **High-Quality EPUB Generation**: Creates well-structured EPUB files with proper metadata and navigation
- **Parallel Processing**: Processes multiple PDF pages simultaneously for improved performance
- **Error Handling**: Implements comprehensive error handling with fallback mechanisms
- **User-Friendly Web Interface**: Provides a simple web interface for file upload and conversion

## Installation

### Prerequisites

- Python 3.7+
- Virtual environment (recommended)

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pdf2epub_ai
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   # Create .env file
   touch .env
   # Add your OpenAI API key
   echo "OPENAI_API_KEY=your-api-key" >> .env
   # Set LLM model (optional, default: gpt-4o)
   echo "LLM_MODEL=gpt-4o" >> .env
   # Enable/disable LLM (optional, default: True)
   echo "LLM_ENABLED=True" >> .env
   ```

## Usage

### Web Interface

1. Start the web server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to `http://localhost:8000`

3. Upload a PDF file and configure conversion options

4. Click "Convert" to generate EPUB

5. Download the generated EPUB file

### Command Line

```bash
# Basic usage
python -m app.utils.pdf_processor --input input.pdf --output output.epub

# With custom title and author
python -m app.utils.pdf_processor --input input.pdf --output output.epub --title "Book Title" --author "Author Name"
```

## API Documentation

### Endpoints

- **GET /**: Web interface
- **POST /convert**: Convert PDF to EPUB
  - **Request**: Multipart form with file, title, author, and llm_api_key
  - **Response**: EPUB file download or error message

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| LLM_ENABLED | Enable AI-powered features | True |
| LLM_API_KEY | OpenAI API key | - |
| LLM_MODEL | LLM model to use | gpt-4o |
| UPLOAD_FOLDER | Directory for uploaded files | ./uploads |
| OUTPUT_FOLDER | Directory for generated EPUB files | ./output |

## Project Structure

```
pdf2epub_ai/
├── app/
│   ├── static/           # Static files
│   ├── templates/        # HTML templates
│   ├── utils/            # Utility modules
│   │   ├── document_extractor.py  # PDF extraction
│   │   ├── epub_generator.py      # EPUB generation
│   │   ├── llm_processor.py       # LLM integration
│   │   ├── logger.py              # Logging
│   │   └── pdf_processor.py       # PDF processing
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI application
├── venv/                 # Virtual environment
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## Dependencies

- **PyMuPDF**: PDF text extraction
- **EbookLib**: EPUB generation
- **OpenAI**: LLM integration
- **FastAPI**: Web framework
- **Jinja2**: Template engine
- **python-dotenv**: Environment variables

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

MIT

## Acknowledgements

- [Parth844/AI_pdf_to_Epub](https://github.com/Parth844/AI_pdf_to_Epub) - For AI-powered structure detection
- [mindsdb/aipdf](https://github.com/mindsdb/aipdf) - For parallel processing implementation
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - For PDF text extraction
- [EbookLib](https://github.com/aerkalov/ebooklib) - For EPUB generation
- [OpenAI](https://openai.com/) - For LLM integration
