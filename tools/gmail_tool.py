# tools/gmail_tool.py

# os: helps Python interact with the operating system
import os
# sys: helps Python find files in other folders
import sys
# base64: Gmail sends email content encoded in base64, we need to decode it
import base64
# Google API libraries for authentication and Gmail access
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# This tells Python to also look in the parent folder (professor_agent/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import paths we set in config.py
from config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH

# SCOPES tells Google what permissions we need
# readonly means we can only READ emails, not send or delete
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """Authenticates with Gmail and returns a service object we can use to read emails."""

    # creds will hold our authentication token
    creds = None

    # token.json stores the access token after first login
    # if it exists, load it so user doesn't have to log in every time
    if os.path.exists(GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, SCOPES)

    # if token doesn't exist or has expired, get a new one
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # automatically refresh the token if it's expired
            creds.refresh(Request())
        else:
            # first time: open browser for user to log in to Google
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # save the token so we don't have to log in next time
        with open(GMAIL_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    # build and return the Gmail service object
    return build("gmail", "v1", credentials=creds)


def get_unread_emails(max_results: int = 10) -> list[dict]:
    """Fetches unread emails from Gmail inbox and returns them as a list."""

    # get the Gmail service
    service = get_gmail_service()

    # search for unread emails in inbox
    # q="is:unread" is the same as typing "is:unread" in Gmail search bar
    results = service.users().messages().list(
        userId="me",
        q="is:unread in:inbox",
        maxResults=max_results
    ).execute()

    # get the list of messages, empty list if none found
    messages = results.get("messages", [])

    # this will hold the full email data
    emails = []

    for message in messages:
        # fetch full email details using the message id
        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        # extract the email headers (subject, sender, date)
        headers = msg["payload"]["headers"]

        # find specific headers we need
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "제목 없음")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "발신자 없음")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "날짜 없음")

        # extract the email body text
        body = extract_body(msg["payload"])

        # get list of attachments if any
        attachments = extract_attachments(msg["payload"])

        # add this email to our list as a dictionary
        emails.append({
            "id": message["id"],        # unique Gmail message ID
            "subject": subject,          # email subject
            "sender": sender,            # who sent it
            "date": date,                # when it was sent
            "body": body,                # email body text
            "attachments": attachments   # list of attachments
        })

    return emails


def extract_body(payload: dict) -> str:
    """Extracts the plain text body from an email payload."""

    body = ""

    # some emails have multiple parts (plain text + HTML)
    if "parts" in payload:
        for part in payload["parts"]:
            # we only want plain text, not HTML
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    # decode from base64 to regular text
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
    else:
        # simple email with no parts
        data = payload["body"].get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8")

    return body


def extract_attachments(payload: dict) -> list[str]:
    """Returns a list of attachment filenames from an email."""

    attachments = []

    # check if email has multiple parts
    if "parts" in payload:
        for part in payload["parts"]:
            # if part has a filename, it's an attachment
            if part.get("filename"):
                attachments.append(part["filename"])

    # return "없음" if no attachments found
    return attachments if attachments else ["없음"]