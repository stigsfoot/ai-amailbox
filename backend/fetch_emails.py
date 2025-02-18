import base64
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import logging

load_dotenv()
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_gmail():
    # TODO: Load and return OAuth2 credentials.
    creds = ...  # Set up your credentials here.
    return build("gmail", "v1", credentials=creds)

def fetch_usps_email(service):
    """
    Fetches USPS Informed Delivery emails, extracts JPEG attachments,
    saves them under ./mail_images, and returns a list of file paths.
    """
    image_files = []
    try:
        results = service.users().messages().list(
            userId="me", q="subject:'Informed Delivery Daily Digest'"
        ).execute()
        messages = results.get("messages", [])
        logger.info("Found %d messages", len(messages))
        for msg in messages:
            message = service.users().messages().get(userId="me", id=msg["id"]).execute()
            for part in message.get("payload", {}).get("parts", []):
                if part.get("mimeType") == "image/jpeg" and "data" in part.get("body", {}):
                    image_data = base64.urlsafe_b64decode(part["body"]["data"])
                    filename = f"./mail_images/{msg['id']}.jpg"
                    with open(filename, "wb") as img_file:
                        img_file.write(image_data)
                    image_files.append(filename)
                    logger.info("Saved image: %s", filename)
    except HttpError as error:
        logger.error("An error occurred: %s", error)
    return image_files

if __name__ == "__main__":
    service = authenticate_gmail()
    images = fetch_usps_email(service)
    if images:
        print("Fetched images:", images)
    else:
        print("No images fetched.")