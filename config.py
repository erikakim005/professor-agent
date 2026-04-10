import os 
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()   # reads your .env file 

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Gmail
GMAIL_CREDENTIALS_PATH = "credentials.json" 
GMAIL_TOKEN_PATH = "token.json"

# Obsidian
# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Gmail
GMAIL_CREDENTIALS_PATH = "credentials.json"
GMAIL_TOKEN_PATH = "token.json"

# Obsidian
OBSIDIAN_VAULT = Path("/Users/erika/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault")
OBSIDIAN_EMAIL_FOLDER = OBSIDIAN_VAULT / "이메일"

# Agent settings
MODEL = "claude-opus-4-6"
POLL_INTERVAL_MINUTES = 5

# Email categories
CATEGORIES = [
    "학생문의",
    "논문",
    "행정",
    "마케팅",
    "협업제안",
    "기타"
]

# file that stores IDs of emails we already processed
PROCESSED_IDS_PATH = "processed_ids.txt"