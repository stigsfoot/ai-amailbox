import logging
from dotenv import load_dotenv
import litellm
import os
import json
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIL_IMAGES_PATH = Path("backend/mail_images")
CLASSIFICATION_LOG = Path("backend/classified_mails.json")

def load_classification_cache():
    """Load previously classified mail texts to avoid redundant API calls."""
    if CLASSIFICATION_LOG.exists():
        with open(CLASSIFICATION_LOG, "r") as f:
            return json.load(f)
    return {}

def save_classification_cache(cache):
    """Save classified mail texts to avoid reprocessing."""
    with open(CLASSIFICATION_LOG, "w") as f:
        json.dump(cache, f, indent=4)

def extract_text_from_image(image_path: str) -> str:
    """
    Placeholder function to extract text from an image.
    This should be replaced with an actual OCR solution (Tesseract, Google Vision, etc.).

    Args:
        image_path (str): The path to the mail image.

    Returns:
        str: Simulated extracted text from the mail image.
    """
    logger.info("Extracting text from image: %s", image_path)
    return f"Sample extracted text from {image_path}"  # Simulate extracted text for now

import logging
from dotenv import load_dotenv
import litellm
import os
import json
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIL_IMAGES_PATH = Path("backend/mail_images")
CLASSIFICATION_LOG = Path("backend/classified_mails.json")

import logging
from dotenv import load_dotenv
import litellm
import os
import json
import re
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIL_IMAGES_PATH = Path("backend/mail_images")
CLASSIFICATION_LOG = Path("backend/classified_mails.json")

import logging
import time
from dotenv import load_dotenv
import litellm
import os
import json
import re
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIL_IMAGES_PATH = Path("backend/mail_images")
CLASSIFICATION_LOG = Path("backend/classified_mails.json")

def classify_mail(image_path: str, max_retries=3) -> dict:
    """
    Classifies a given mail image as 'Important', 'Spam', or 'Unknown' using the Gemini AI model.

    Args:
        image_path (str): The path to the mail image that needs to be classified.
        max_retries (int): Number of retries if API returns a 503 error.

    Returns:
        dict: A dictionary containing:
            - classification (str): 'Important', 'Spam', or 'Unknown'.
            - confidence (float): A confidence score between 0.0 and 1.0.
            - reasoning (str): A short explanation of why the classification was made.
    """
    logger.info("Classifying mail image: %s...", image_path)

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        messages = [
            {"role": "system", "content": (
                "You are an AI that classifies postal mail into 'Important', 'Spam', or 'Unknown' "
                "based on its content and sender. Consider the text, sender, and any visual elements."
                "Provide a JSON response with the following structure:\n"
                "{\n"
                '  "classification": "Important" | "Spam" | "Unknown",\n'
                '  "confidence": float between 0.0 and 1.0,\n'
                '  "reasoning": "Explanation of why this classification was made."\n'
                "}"
            )},
            {
                "role": "user",
                "content": "Classify the following mail piece. Return JSON format only.",
                "images": [image_data]  # ✅ Pass the image directly
            }
        ]

        retries = 0
        while retries < max_retries:
            try:
                response = litellm.completion(
                    model=os.getenv("LITELLM_MODEL", "gemini-1.5-pro"),
                    api_key=os.getenv("GEMINI_API_KEY"),
                    provider=os.getenv("LITELLM_PROVIDER", "google/ai-studio"),
                    messages=messages,
                )
                break  # ✅ If successful, exit retry loop
            except litellm.InternalServerError as e:
                if "503" in str(e):
                    logger.warning("Gemini API is overloaded. Retrying in %d seconds...", 2**retries)
                    time.sleep(2**retries)  # Exponential backoff
                    retries += 1
                else:
                    raise e  # ✅ If another error occurs, raise it

        raw_result = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        # ✅ Clean and extract valid JSON
        cleaned_result = re.sub(r"```json\n|\n```", "", raw_result).strip()

        try:
            classification_data = json.loads(cleaned_result)
            if not isinstance(classification_data, dict) or "classification" not in classification_data:
                raise ValueError("Invalid response format")
        except json.JSONDecodeError:
            logger.error("AI response was not valid JSON: %s", raw_result)
            classification_data = {"classification": "Error", "confidence": 0.0, "reasoning": "Unable to classify mail"}

        logger.info("LLM classification result: %s", classification_data)
        return classification_data

    except Exception as e:
        logger.error("Failed to classify mail: %s", e)
        return {"classification": "Error", "confidence": 0.0, "reasoning": "Unable to classify mail"}


def process_new_mail_images():
    """Process only new mail images and classify them directly with Gemini."""
    classification_cache = {}

    for image_path in MAIL_IMAGES_PATH.glob("*.jpg"):  # ✅ Process only JPG images
        if str(image_path) in classification_cache:
            logger.info("Skipping already classified mail: %s", image_path)
            continue  # ✅ Skip already processed images

        classification = classify_mail(str(image_path))

        # ✅ Cache the classification result
        classification_cache[str(image_path)] = classification

        logger.info("Processed mail image: %s -> %s", image_path, classification)

if __name__ == "__main__":
    process_new_mail_images()
