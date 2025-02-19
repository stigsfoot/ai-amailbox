import os
import base64
import logging
import pickle
import requests
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from bs4 import BeautifulSoup


load_dotenv()
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_PATH = Path("backend/token.json")
CREDENTIALS_PATH = Path("backend/credentials.json")

def authenticate_gmail():
    """
    Handles Gmail OAuth authentication:
    - Loads saved tokens (if available).
    - Refreshes tokens if expired.
    - Prompts user for login if no valid credentials exist.

    Returns:
        Gmail API service object.
    """
    creds = None

    # Load existing token if available
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)
        logger.info("Loaded saved credentials from token.json")

    # If no valid credentials, authenticate user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed expired token")
            except Exception as e:
                logger.error("Token refresh failed: %s", e)
        else:
            logger.info("No valid credentials found, prompting user login...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GMAIL_SCOPES)

            # ✅ Force the correct redirect URI
            creds = flow.run_local_server(
                port=8080,  # Ensure this matches the Google Cloud Console setting
                redirect_uri_trailing_slash=False  # Prevents Google from appending extra slashes
            )
            logger.info("Successfully authenticated Gmail API")

        # Save new token for future use
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
            logger.info("Saved credentials to token.json")

    return build("gmail", "v1", credentials=creds)

def fetch_usps_email(service, dry_run=True):
    """
    Fetches USPS Informed Delivery emails with a flexible subject line.
    Extracts raw email content for image filtering.
    If dry_run=True, it will preview matching emails **without downloading images**.
    """
    image_files = []
    try:
        query = "subject:'Your Daily Digest for'"
        results = service.users().messages().list(
            userId="me", q=query, maxResults=5
        ).execute()
        messages = results.get("messages", [])

        logger.info("Found %d USPS Daily Digest emails", len(messages))

        for msg in messages:
            message = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()

            # Extract the raw HTML body
            email_payload = message.get("payload", {})
            email_parts = email_payload.get("parts", [])

            html_body = None

            if "parts" in email_payload:
                # Look for text/html parts
                for part in email_parts:
                    if part.get("mimeType") == "text/html" and "data" in part.get("body", {}):
                        html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
            elif "body" in email_payload and "data" in email_payload["body"]:
                # If no parts exist, check if the entire email is a single HTML message
                html_body = base64.urlsafe_b64decode(email_payload["body"]["data"]).decode("utf-8")

            if not html_body:
                logger.warning("No HTML body found for email %s", msg["id"])
                continue

            logger.info("Extracting correct images from email HTML.")
            correct_images = extract_correct_images(html_body)

            if dry_run:
                logger.info("Skipping image extraction in dry-run mode.")
                continue  # Skip downloading images

            # Extract only correct images
            for img in correct_images:
                image_url = img["src"]

                if image_url.startswith("data:image/jpeg;base64,"):
                    # Handle base64 images
                    image_data = base64.urlsafe_b64decode(image_url.split(",")[1])
                elif image_url.startswith("http"):
                    # Download the image from a URL
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        image_data = response.content
                    else:
                        logger.warning("Failed to download image from URL: %s", image_url)
                        continue
                else:
                    logger.warning("Unknown image format: %s", image_url)
                    continue

                filename = f"./mail_images/{msg['id']}.jpg"

                # Ensure the directory exists
                os.makedirs("./mail_images", exist_ok=True)

                with open(filename, "wb") as img_file:
                    img_file.write(image_data)

                image_files.append(filename)
                logger.info("Saved image: %s", filename)


    except HttpError as error:
        logger.error("An error occurred: %s", error)

    return image_files


def extract_correct_images(html_body):
    """
    Extracts only the correct mail images from the USPS email body.
    Identifies the position of "Do more with your mail" and filters images accordingly.
    """
    soup = BeautifulSoup(html_body, "html.parser")

    # Find all images
    all_images = soup.find_all("img")

    # Locate the section containing "Do more with your mail"
    mail_section = None
    for tag in soup.find_all(["p", "div", "span"]):  # Search in common text containers
        if "do more with your mail" in tag.get_text(strip=True).lower():
            mail_section = tag
            break

    # If we can't find the section, return all images (fallback)
    if not mail_section:
        logger.warning("Could not locate 'Do more with your mail' section. Returning all images.")
        return all_images

    # Only keep images that appear before this section
    correct_images = []
    for img in all_images:
        if mail_section in img.find_all_next():  # Stop when we reach "Do more with your mail"
            break
        correct_images.append(img)

    logger.info("Filtered %d correct mail images", len(correct_images))
    return correct_images


if __name__ == "__main__":
    service = authenticate_gmail()
    images = fetch_usps_email(service)
    if images:
        print("Fetched images:", images)
    else:
        print("No images fetched.")