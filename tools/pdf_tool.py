# tools/pdf_tool.py

# fitz is the library name for PyMuPDF
# PyMuPDF lets us open and read PDF files
import fitz
# os and sys: help Python find files in other folders
import os
import sys
# base64: Gmail sends attachments encoded in base64, we need to decode them
import base64

# This tells Python to also look in the parent folder (professor_agent/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extract_text_from_pdf_file(pdf_path: str) -> str:
    """Opens a PDF file from disk and extracts all text from it."""

    # open the PDF file
    doc = fitz.open(pdf_path)

    # this will hold all the text from every page
    full_text = ""

    # loop through every page in the PDF
    for page in doc:
        # extract text from this page and add it to full_text
        # strip() removes extra whitespace at the start and end
        full_text += page.get_text().strip() + "\n\n"

    # close the PDF file when done
    doc.close()

    return full_text


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts text from a PDF that came as raw bytes (e.g. from Gmail attachment)."""

    # open PDF directly from bytes in memory (no need to save to disk first)
    # stream=pdf_bytes tells fitz to read from memory
    # filetype="pdf" tells fitz what kind of file it is
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    full_text = ""

    for page in doc:
        full_text += page.get_text().strip() + "\n\n"

    doc.close()

    return full_text


def get_pdf_attachment_from_gmail(service, message_id: str, attachment_id: str) -> bytes:
    """Downloads a PDF attachment from Gmail and returns it as bytes."""

    # fetch the attachment data from Gmail API
    attachment = service.users().messages().attachments().get(
        userId="me",
        messageId=message_id,
        id=attachment_id
    ).execute()

    # Gmail encodes attachments in base64 URL-safe format
    # we need to decode it back to raw bytes
    pdf_bytes = base64.urlsafe_b64decode(attachment["data"])

    return pdf_bytes


def process_pdf_attachment(service, message_id: str, part: dict) -> str:
    """Takes a Gmail message part that is a PDF and returns its text content."""

    # get the attachment ID from the message part
    attachment_id = part["body"]["attachmentId"]

    # get the filename so we know what we're processing
    filename = part.get("filename", "unknown.pdf")

    print(f"📄 PDF 읽는 중: {filename}")

    # download the PDF bytes from Gmail
    pdf_bytes = get_pdf_attachment_from_gmail(service, message_id, attachment_id)

    # extract text from the PDF bytes
    text = extract_text_from_pdf_bytes(pdf_bytes)

    # return the filename and extracted text together
    return f"[PDF: {filename}]\n{text}"