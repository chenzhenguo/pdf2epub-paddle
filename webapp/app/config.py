import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Directories
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "outputs")

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# API Configuration
API_URL = "https://s9a8lfu1jd2efbl7.aistudio-app.com/layout-parsing"
API_TOKEN = os.getenv("PADDLE_API_TOKEN", "")

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_ENABLED = bool(LLM_API_KEY)

# Processing Configuration
CHUNK_SIZE = 5  # Reduced to 5 for maximum reliability
MAX_DAILY_PAGES = 3000
