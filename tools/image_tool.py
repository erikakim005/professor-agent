# tools/image_tool.py

# base64: converts image bytes to text so we can send it to Claude API
import base64
# os and sys: help Python find files in other folders
import os
import sys
# mimetypes: detects what kind of image file it is (jpg, png, etc.)
import mimetypes

# This tells Python to also look in the parent folder (professor_agent/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Converts raw image bytes into a base64 string so Claude API can read it."""

    # base64 encoding converts binary data into a text string
    # Claude API requires images to be in this format
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def get_image_media_type(filename: str) -> str:
    """Figures out the image type (jpeg, png, gif, webp) from the filename."""

    # mimetypes.guess_type returns something like ("image/jpeg", None)
    # we only need the first part
    mime_type, _ = mimetypes.guess_type(filename)

    # if we can't detect it, default to jpeg
    if not mime_type:
        return "image/jpeg"

    return mime_type


def prepare_image_for_claude(image_bytes: bytes, filename: str) -> dict:
    """Prepares an image in the exact format Claude API expects."""

    # convert image to base64 string
    image_data = encode_image_to_base64(image_bytes)

    # get the image type (jpeg, png, etc.)
    media_type = get_image_media_type(filename)

    # Claude API requires this exact structure to receive an image
    # type: "image" tells Claude this is an image, not text
    # source: contains the actual image data
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": image_data
        }
    }


def get_image_attachment_from_gmail(service, message_id: str, attachment_id: str) -> bytes:
    """Downloads an image attachment from Gmail and returns it as bytes."""

    # fetch the attachment data from Gmail API
    attachment = service.users().messages().attachments().get(
        userId="me",
        messageId=message_id,
        id=attachment_id
    ).execute()

    # Gmail encodes attachments in base64 URL-safe format
    # we need to decode it back to raw bytes
    image_bytes = base64.urlsafe_b64decode(attachment["data"])

    return image_bytes


def process_image_attachment(service, message_id: str, part: dict) -> dict:
    """Takes a Gmail message part that is an image and prepares it for Claude."""

    # get the attachment ID from the message part
    attachment_id = part["body"]["attachmentId"]

    # get the filename so we know what type of image it is
    filename = part.get("filename", "image.jpg")

    print(f"🖼️ 이미지 읽는 중: {filename}")

    # download the image bytes from Gmail
    image_bytes = get_image_attachment_from_gmail(service, message_id, attachment_id)

    # prepare the image in Claude API format
    return prepare_image_for_claude(image_bytes, filename)