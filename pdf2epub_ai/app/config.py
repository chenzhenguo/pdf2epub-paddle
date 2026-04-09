import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Directories
    UPLOAD_FOLDER: str = os.path.join(os.getcwd(), "uploads")
    OUTPUT_FOLDER: str = os.path.join(os.getcwd(), "output")
    
    # LLM settings
    LLM_ENABLED: bool = True
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    
    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()

# Export settings
UPLOAD_FOLDER = settings.UPLOAD_FOLDER
OUTPUT_FOLDER = settings.OUTPUT_FOLDER
LLM_ENABLED = settings.LLM_ENABLED
LLM_API_KEY = settings.LLM_API_KEY
LLM_MODEL = settings.LLM_MODEL