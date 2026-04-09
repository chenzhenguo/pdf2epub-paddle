# PDF to EPUB Converter Web App

A web application that converts PDF files to EPUB format using PyMuPDF for text extraction and intelligent structure detection.

## Features

- **No OCR**: Directly extracts underlying PDF text
- **Smart Structure Detection**: Uses heuristics to detect book structure (titles, chapters, etc.)
- **Responsive Web Interface**: User-friendly interface that works on different devices
- **Customizable Options**: Allows users to set book title, author, and TOC generation options
- **Fast Processing**: Efficient PDF processing and EPUB generation

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd pdf2epub-webapp
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the development server:

```bash
python run.py
```

2. Open your browser and navigate to `http://localhost:8000`

### Usage

1. Upload your PDF file
2. Enter your PaddleOCR API token (currently not used, but required for future features)
3. Optional: Enter book title and author
4. Select TOC generation options
5. Click "Convert to EPUB"
6. Download the generated EPUB file

## Deployment

### Heroku

1. Create a new Heroku app
2. Connect your GitHub repository
3. Set up automatic deployments
4. Add a `Procfile` to the root directory (already provided)
5. Deploy the application

### Other Platforms

The application can be deployed to any platform that supports Python web applications, such as:
- Vercel
- AWS Elastic Beanstalk
- Google Cloud Platform
- DigitalOcean App Platform

## Project Structure

```
webapp/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration
│   ├── templates/       # HTML templates
│   │   └── index.html   # Main page
│   ├── static/          # Static files
│   │   └── style.css    # CSS styles
│   └── utils/           # Utility functions
│       ├── pdf_processor.py     # PDF processing
│       └── epub_generator.py    # EPUB generation
├── run.py              # Development server
├── requirements.txt    # Dependencies
├── Procfile            # Deployment configuration
└── .gitignore          # Git ignore file
```

## Technologies Used

- **Backend**: FastAPI, Python
- **PDF Processing**: PyMuPDF
- **EPUB Generation**: EbookLib
- **Frontend**: HTML, CSS
- **Template Engine**: Jinja2

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
