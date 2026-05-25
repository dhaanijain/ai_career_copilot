"""
app/config.py — AI Career Copilot
Loads and validates environment variables for external API credentials.

Usage:
    from app.config import APP_ID, APP_KEY
"""

import os

from dotenv import load_dotenv

load_dotenv()

APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")

if not APP_ID or not APP_KEY:
    raise EnvironmentError(
        "Missing Adzuna API credentials. "
        "Please configure ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file."
    )
