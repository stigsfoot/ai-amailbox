import os
import base64
import logging
from pathlib import Path
import requests
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
PROCESSED_EMAILS_FILE = "backend/processed_emails.txt"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_PATH = Path("backend/token.json")
CREDENTIALS_PATH = Path("backend/credentials.json")

def authenticate_gmail():
    """Handles Gmail OAuth authentication and returns the Gmail API service object."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)
        logger.info("Loaded saved credentials from token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("Refreshed expired token")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GMAIL_SCOPES)
            creds = flow.run_local_server(port=8080)
            logger.info("Successfully authenticated Gmail API")

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
            logger.info("Saved credentials to token.json")

    return build("gmail", "v1", credentials=creds)

def load_processed_emails():
    """Load previously processed email IDs to avoid fetching the same emails."""
    if os.path.exists(PROCESSED_EMAILS_FILE):
        with open(PROCESSED_EMAILS_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_processed_email(email_id):
    """Save processed email IDs to avoid re-fetching."""
    with open(PROCESSED_EMAILS_FILE, "a") as f:
        f.write(email_id + "\n")

import time

def fetch_usps_email(service, dry_run=True):
    """Fetch USPS Informed Delivery emails and extract mail images."""
    processed_emails = load_processed_emails()
    results = service.users().messages().list(userId="me", q="subject:'Your Daily Digest for'", maxResults=3).execute()
    messages = results.get("messages", [])

    logger.info("Found %d USPS Daily Digest emails", len(messages))

    image_files = []
    for msg in messages:
        if msg["id"] in processed_emails:
            logger.info("Skipping already processed email: %s", msg["id"])
            continue

        message = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        email_payload = message.get("payload", {})
        email_parts = email_payload.get("parts", [])

        html_body = None
        for part in email_parts:
            if part.get("mimeType") == "text/html" and "data" in part.get("body", {}):
                html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

        if not html_body:
            logger.warning("No HTML body found for email %s. Checking plain text version...", msg["id"])
            for part in email_parts:
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    text_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    logger.info("Plain text content found for email %s: %s", msg["id"], text_body[:100])  # Show first 100 chars
                    break  # Stop once text is found

            continue  # Skip processing this email

        save_processed_email(msg["id"])


def extract_attachments(service, message_id, part, attachments):
    """Recursively extract image attachments from email parts."""
    if "parts" in part:
        for sub_part in part["parts"]:
            extract_attachments(service, message_id, sub_part, attachments)

    if part.get("mimeType", "").startswith("image/") and "body" in part and "attachmentId" in part["body"]:
        cid = next((header["value"].strip("<>") for header in part.get("headers", []) if header["name"].lower() == "content-id"), None)

        if cid:
            attachments[cid] = fetch_attachment(service, message_id, part["body"]["attachmentId"])

def extract_correct_image_cids(html_body):
    """
    Extracts correct mail image CIDs or direct image URLs.
    Filters out tracking pixels, USPS branding, and non-mail images.
    """
    soup = BeautifulSoup(html_body, "html.parser")
    all_images = soup.find_all("img")

    correct_images = []
    for img in all_images:
        src = img.get("src", "")

        # 🚨 Skip tracking pixels
        if any(kw in src for kw in ["pixel.watch", "tracking", "emailRead"]):
            logger.warning("Skipping tracking pixel: %s", src)
            continue

        # 🚨 Skip USPS branding images
        if any(kw in src for kw in ["uspslogo", "icon-envelope", "packages-icon", "refer-friends"]):
            logger.info("Skipping USPS branding image: %s", src)
            continue

        # ✅ Only collect real mail images (usually contain mailpiece identifiers)
        if "mailpiece" in src or "mailid" in src or "fur=ip" in src:
            correct_images.append(src)

    logger.info("Filtered %d valid mail images", len(correct_images))
    return correct_images

 

def fetch_attachment(service, message_id, attachment_id):
    """Fetches an email attachment from Gmail API using attachment_id."""
    try:
        attachment = service.users().messages().attachments().get(
            userId="me", messageId=message_id, id=attachment_id
        ).execute()
        return base64.urlsafe_b64decode(attachment["data"])
    except Exception as e:
        logger.error("Failed to fetch attachment for message %s: %s", message_id, e)
        return None

if __name__ == "__main__":
    service = authenticate_gmail()
    images = fetch_usps_email(service, dry_run=False)
    if images:
        print("Fetched images:", images)
    else:
        print("No images fetched.")