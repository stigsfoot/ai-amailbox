import base64
import os
from dotenv import load_dotenv
import litellm
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> str:
    """
    Reads an image, encodes it in base64, and calls Gemini via LiteLLM
    to extract text (OCR) from the mail image.
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this mail image."},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                ]
            }
        ]
        model = os.getenv("LITELLM_MODEL", "gemini-1.5-pro")
        response = litellm.completion(
            model=model,
            api_key=os.getenv("LITELLM_API_KEY"),
            provider=os.getenv("LITELLM_PROVIDER", "google/ai-studio"),
            messages=messages,
        )
        extracted = response["choices"][0]["message"]["content"]
        logger.info("Extracted text: %s", extracted)
        return extracted
    except Exception as e:
        logger.error("Error extracting text from image %s: %s", image_path, e)
        return ""

if __name__ == "__main__":
    sample_image = "./mail_images/example.jpg"
    text = extract_text_from_image(sample_image)
    print("Extracted text:", text)
