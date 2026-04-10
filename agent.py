# agent.py

# anthropic: the official Python library to talk to Claude API
import anthropic
# json: helps us parse structured data from Claude's responses
import json
# os and sys: help Python find files in other folders
import os
import sys
# datetime: helps us format dates and times
from datetime import datetime

# This tells Python to also look in the current folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# import our config settings
from config import ANTHROPIC_API_KEY, MODEL, CATEGORIES, PROCESSED_IDS_PATH

# import all our tools
from tools.gmail_tool import get_gmail_service, get_unread_emails
from tools.pdf_tool import process_pdf_attachment
from tools.image_tool import process_image_attachment
from tools.obsidian_tool import save_email_note

# create the Anthropic client using our API key
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def analyze_email(email: dict) -> dict:
    
    """
    Sends an email to Claude and asks it to:
    1. Summarize it in Korean
    2. Assign a category
    3. Extract todo items
    Returns a dictionary with the analysis results.
    """

    print(f"\n🤖 Claude가 분석 중: {email['subject']}")

    # build the message content list
    # this will contain text + any images if present
    content = []

    # add the main email text as the first message
    content.append({
        "type": "text",
        "text": f"""다음 이메일을 분석해줘.

발신자: {email['sender']}
날짜: {email['date']}
제목: {email['subject']}

본문:
{email['body']}

아래 JSON 형식으로만 답해줘. 다른 말은 하지 마:
{{
    "category": "카테고리 (반드시 다음 중 하나: {', '.join(CATEGORIES)})",
    "summary": "한국어로 2-3문장 요약",
    "todos": ["할일1", "할일2"],
    "attachment_summary": "첨부파일 요약 (없으면 없음)"
}}"""
    })

    # if email has image attachments, add them to the content
    # so Claude can visually analyze them too
    if email.get("image_contents"):
        for image_content in email["image_contents"]:
            # add the image in Claude API format
            content.append(image_content)
        # tell Claude to also analyze the images
        content.append({
            "type": "text",
            "text": "위 이미지들도 함께 분석해서 JSON에 포함해줘."
        })

    # if email has PDF text, add it to the content
    if email.get("pdf_texts"):
        for pdf_text in email["pdf_texts"]:
            content.append({
                "type": "text",
                "text": f"\n첨부된 PDF 내용:\n{pdf_text}"
            })

    # send everything to Claude and get a response
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        # system prompt tells Claude its role and how to behave
        system="""너는 교수님의 이메일 비서야. 
이메일을 분석해서 반드시 JSON 형식으로만 답해야 해.
절대 JSON 외에 다른 텍스트를 추가하지 마.""",
        messages=[
            {"role": "user", "content": content}
        ]
    )

    # extract the text response from Claude
    result_text = response.content[0].text

    # parse the JSON response from Claude
    # Claude should have returned pure JSON based on our instructions
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError:
        # if Claude added extra text, try to find the JSON part
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # fallback if JSON parsing fails completely
            result = {
                "category": "기타",
                "summary": result_text,
                "todos": [],
                "attachment_summary": "없음"
            }

    return result


def process_email_attachments(email: dict) -> dict:
    """
    Downloads and processes all attachments from an email.
    PDFs get text extracted, images get prepared for Claude vision.
    Returns updated email dict with attachment contents added.
    """

    # skip if no attachments
    if email["attachments"] == ["없음"]:
        return email

    print(f"📎 첨부파일 처리 중: {email['attachments']}")

    # get Gmail service to download attachments
    service = get_gmail_service()

    # fetch the full Gmail message to get attachment data
    msg = service.users().messages().get(
        userId="me",
        id=email["id"],
        format="full"
    ).execute()

    # lists to store processed attachment contents
    pdf_texts = []
    image_contents = []

    # loop through all parts of the email
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            filename = part.get("filename", "")
            mime_type = part.get("mimeType", "")

            # check if this part is a PDF
            if filename.endswith(".pdf") or mime_type == "application/pdf":
                pdf_text = process_pdf_attachment(service, email["id"], part)
                pdf_texts.append(pdf_text)

            # check if this part is an image
            elif mime_type.startswith("image/"):
                image_content = process_image_attachment(service, email["id"], part)
                image_contents.append(image_content)

    # add the processed contents to the email dict
    email["pdf_texts"] = pdf_texts
    email["image_contents"] = image_contents

    return email


def format_date_time(raw_date: str):
    """Extracts clean date and time from Gmail's raw date string."""

    try:
        from email.utils import parsedate_to_datetime
        import zoneinfo

        dt = parsedate_to_datetime(raw_date)

        # convert to Korea timezone (UTC+9)
        korea_tz = zoneinfo.ZoneInfo("Asia/Seoul")
        dt = dt.astimezone(korea_tz)

        # format date as YYYY-MM-DD
        date = dt.strftime("%Y-%m-%d")
        # format time as HHMM (e.g. 1333)
        time = dt.strftime("%H%M")
    except:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H%M")

    return date, time


def run_agent():
    """
    Main agent loop:
    1. Fetch unread emails from Gmail
    2. Skip already processed emails
    3. Process attachments (PDF, images)
    4. Send to Claude for analysis
    5. Save results to Obsidian
    6. Mark email as processed
    """

    print("🚀 교수님 이메일 에이전트 시작!")

    # load already processed email IDs from file
    # so we never process the same email twice
    if os.path.exists(PROCESSED_IDS_PATH):
        with open(PROCESSED_IDS_PATH, "r") as f:
            processed_ids = set(f.read().splitlines())
    else:
        # first time running, no processed emails yet
        processed_ids = set()

    # fetch unread emails (max 10 at a time)
    emails = get_unread_emails(max_results=10)

    if not emails:
        print("📭 새 이메일 없음")
        return

    # filter out already processed emails
    new_emails = [e for e in emails if e["id"] not in processed_ids]

    if not new_emails:
        print("📭 새로 처리할 이메일 없음 (모두 이미 처리됨)")
        return

    print(f"📬 {len(new_emails)}개의 새 이메일 발견!")

    # process each email one by one
    for email in new_emails:
        try:
            # step 1: process any attachments first
            email = process_email_attachments(email)

            # step 2: send to Claude for analysis
            analysis = analyze_email(email)

            # step 3: format the date and time cleanly
            date, time = format_date_time(email["date"])

            # step 4: determine attachment info for the note
            attachment_info = "없음"
            if email["attachments"] != ["없음"]:
                attachment_info = ", ".join(email["attachments"])

            # step 5: save the result to Obsidian
            saved_path = save_email_note(
                subject=email["subject"],
                sender=email["sender"],
                date=date,
                time=time,
                category=analysis["category"],
                summary=analysis["summary"],
                todos=analysis["todos"],
                attachment=attachment_info
            )

            print(f"✅ 저장 완료: {saved_path}")

            # step 6: mark this email as processed so we skip it next time
            processed_ids.add(email["id"])
            with open(PROCESSED_IDS_PATH, "a") as f:
                f.write(email["id"] + "\n")

        except Exception as e:
            # if one email fails, log the error and continue with the next
            print(f"❌ 오류 발생 ({email['subject']}): {e}")
            continue

    print("\n🎉 모든 이메일 처리 완료!")