import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
DB_PATH = str(BASE_DIR / "data" / "healthcare_analytics.db")

# Fallback validation
if not GEMINI_API_KEY:
    print("\n[WARNING] GEMINI_API_KEY is not set in your .env file! Please add it.\n")