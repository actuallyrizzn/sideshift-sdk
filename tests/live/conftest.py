"""Pytest configuration for live tests."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from tests/live directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get credentials from environment
ACCOUNT_ID = os.getenv("SIDESHIFT_ACCOUNT_ID")
API_SECRET = os.getenv("SIDESHIFT_API_SECRET")

if not ACCOUNT_ID or not API_SECRET:
    raise ValueError(
        "Missing required environment variables. "
        "Please create a .env file in tests/live/ with SIDESHIFT_ACCOUNT_ID and SIDESHIFT_API_SECRET"
    )
