# tools/obsidian_tool.py

# pathlib: lets us work with file paths in a smart way
from pathlib import Path
# datetime: lets us get the current date and time
from datetime import datetime
# sys and os: help Python find files in other folders
import sys
import os

# This tells Python to also look in the parent folder (professor_agent/)
# because config.py is up one level from tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Obsidian folder path we set in config.py
from config import OBSIDIAN_EMAIL_FOLDER


def save_email_note(
    subject: str,      # email subject line (이메일 제목)
    sender: str,       # who sent the email (발신자)
    date: str,         # date the email was sent (날짜)
    time: str,         # time the email was sent (시간)
    category: str,     # category Claude assigned (학생문의, 논문, etc.)
    summary: str,      # Korean summary Claude wrote
    todos: list[str],  # list of action items Claude extracted
    attachment: str = "없음"  # attachment info, defaults to 없음
) -> str:              # this function returns a string (the file path)

    # Create a subfolder for each category inside 이메일/
    # example: 이메일/학생문의/ or 이메일/논문/
    category_folder = OBSIDIAN_EMAIL_FOLDER / category

    # Create the category folder if it doesn't exist yet
    # parents=True: also creates 이메일/ if missing
    # exist_ok=True: don't crash if folder already exists
    category_folder.mkdir(parents=True, exist_ok=True)

    # remove special characters that Mac doesn't allow in filenames
    # ' ? : * " < > | / \ are all illegal in filenames
    import re
    safe_subject = re.sub(r'[\'?:*"<>|/\\]', '', subject)

    # limit subject to 50 characters to avoid filename too long error
    # if subject is longer than 50 chars, cut it and add "..." at the end
    safe_subject = safe_subject[:50] + "..." if len(safe_subject) > 50 else safe_subject

    # Build the filename using date + time + safe subject
    # example: 2026-04-10_1333_창의적 소프트웨어 프로그래밍...md
    filename = f"{date}_{time}_{safe_subject}.md"

    # Full path = category folder + filename
    # example: 이메일/학생문의/2026-04-10_1333_창의적 소프트웨어...md
    filepath = category_folder / filename

    # Convert the todos list into bullet points
    # example: ["답장하기", "확인하기"] → "* 답장하기\n* 확인하기"
    # if todos list is empty, just write "* 없음"
    todo_lines = "\n".join([f"* {todo}" for todo in todos]) if todos else "* 없음"

    # Build the full markdown content of the note
    # --- section at top is frontmatter: Obsidian reads this for tags and metadata
    # ### 할일: small header (H3)
    content = f"""---
tags: [이메일, {category}]
날짜: {date}
시간: {time}
발신자: {sender}
첨부파일: {attachment}
---

카테고리: {category}

요약: {summary}

첨부파일: {attachment}

### 할일
{todo_lines}
"""

    # Write the content to the file
    # encoding="utf-8" makes sure Korean characters save correctly
    filepath.write_text(content, encoding="utf-8")

    # Return the file path so we know where it was saved
    return str(filepath)