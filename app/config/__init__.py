"""
app/config/__init__.py — AI Career Copilot
Loads and validates all environment variables.

Re-exports Adzuna credentials at the package level so existing imports
(from .config import APP_ID, APP_KEY) continue to work unchanged.
"""

import os

from dotenv import load_dotenv

load_dotenv()

APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")

if not APP_ID or not APP_KEY:
    raise EnvironmentError(
        "Missing Adzuna API credentials. "
        "Configure ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file."
    )
