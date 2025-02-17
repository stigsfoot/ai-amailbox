from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import os
from dotenv import load_dotenv

load_dotenv()
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def fetch_usps_email(service):
    try:
        results = service.users().messages().list(userId="me", q="subject:'Informed Delivery Daily Digest'").execute()
        messages = results.get("messages", [])
        for msg in messages:
            message = service.users().messages().get(userId="me", id=msg["id"]).execute()
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "image/jpeg":
                    image_data = base64.urlsafe_b64decode(part["body"]["data"])
                    with open(f"./mail_images/{msg['id']}.jpg", "wb") as img_file:
                        img_file.write(image_data)
    except HttpError as error:
        print(f"An error occurred: {error}")

def authenticate_gmail():
    creds = ...  # Load OAuth2 credentials (setup required) 
    return build("gmail", "v1", credentials=creds)

if __name__ == "__main__":
    service = authenticate_gmail()
    fetch_usps_email(service)
