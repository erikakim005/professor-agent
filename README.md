# 📧 Professor Email AI Agent

An intelligent email automation system that reads Gmail, summarizes emails in Korean using Claude AI, and automatically saves them to Obsidian — organized by category.

## ✨ Features

- 📬 **Auto Gmail monitoring** — checks for unread emails every 5 minutes
- 🤖 **Claude AI analysis** — summarizes emails in Korean and assigns categories
- 📁 **Auto Obsidian saving** — saves each email as a structured markdown note
- 📂 **Category folders** — automatically sorts emails into subfolders
- 📄 **PDF reading** — extracts and summarizes PDF attachments
- 🖼️ **Image analysis** — Claude visually analyzes image attachments
- 🔁 **No duplicates** — tracks processed emails so nothing is processed twice

## 📂 Project Structure
professor_agent/
├── main.py              # entry point + scheduler
├── agent.py             # Claude AI brain (orchestrator)
├── config.py            # settings and API keys
├── tools/
│   ├── gmail_tool.py    # reads emails from Gmail
│   ├── pdf_tool.py      # extracts text from PDF attachments
│   ├── image_tool.py    # analyzes image attachments
│   └── obsidian_tool.py # saves notes to Obsidian vault
└── .env                 # secret API keys (never upload this!)

## 🗂️ Email Categories

Emails are automatically classified into:
- 학생문의 (Student inquiries)
- 논문 (Research/Papers)
- 행정 (Administration)
- 마케팅 (Marketing)
- 협업제안 (Collaboration)
- 기타 (Other)

## 🛠️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/erikakim005/professor-agent.git
cd professor-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install anthropic google-auth google-auth-oauthlib google-api-python-client pymupdf pillow apscheduler python-dotenv
```

### 4. Set up environment variables
Create a `.env` file:
ANTHROPIC_API_KEY=your-api-key-here

### 5. Set up Gmail API
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Enable Gmail API
- Download `credentials.json` and place it in the project folder

### 6. Configure Obsidian vault path
Edit `config.py` and set your vault path:
```python
OBSIDIAN_VAULT = Path("/your/obsidian/vault/path")
```

### 7. Run
```bash
python main.py
```

## 🏗️ Architecture
Gmail API → Agent Orchestrator (Claude) → Tools → Obsidian
↓
┌─ summarize_email
├─ analyze_pdf
├─ analyze_image
└─ extract_todos

## 🔒 Security

Never upload these files to GitHub:
- `.env` (API keys)
- `credentials.json` (Google auth)
- `token.json` (Gmail token)

These are already in `.gitignore` ✅

## Built With

- [Claude AI](https://anthropic.com) — email analysis and summarization
- [Gmail API](https://developers.google.com/gmail) — email monitoring
- [Obsidian](https://obsidian.md) — knowledge base storage
- [APScheduler](https://apscheduler.readthedocs.io) — automatic scheduling
- [PyMuPDF](https://pymupdf.readthedocs.io) — PDF processing
