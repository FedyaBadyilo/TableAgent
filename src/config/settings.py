# config/settings.py
import os
from dotenv import load_dotenv
from .model_config import ModelConfig

load_dotenv()

class Settings:
    # Google Sheets API
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    
    # API
    API_HOST = os.getenv("API_HOST")
    API_PORT = int(os.getenv("API_PORT"))
    
    # AI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    
    # Test spreadsheet
    SAMPLE_SPREADSHEET_ID = os.getenv("SAMPLE_SPREADSHEET_ID")
    
    # Model configuration
    model_config = ModelConfig()

settings = Settings()