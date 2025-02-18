from smolagents import tool
import logging
from dotenv import load_dotenv
import litellm
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def classify_mail(mail_text: str) -> str:
    """
    Uses the Gemini model to classify mail as 'Important', 'Spam', or 'Unknown'.

    Args:
        mail_text: The extracted text from the mail image that needs to be classified.

    Returns:
        str: The classification result.
    """
    logger.info("Classifying mail text using Gemini...")
    messages = [
        {"role": "system", "content": (
            "You are an AI that classifies mail into 'Important', 'Spam', or 'Unknown' based on content. "
            "Consider contextual cues, sender information, and language nuance." 
        )},
        {"role": "user", "content": f"Please classify the following mail text:\n{mail_text}"}
    ]
    response = litellm.completion(
        model=os.getenv("LITELLM_MODEL", "gemini-1.5-pro"),
        api_key=os.getenv("GEMINI_API_KEY"),
        provider=os.getenv("LITELLM_PROVIDER", "google/ai-studio"),
        messages=messages,
    )
    result = response["choices"][0]["message"]["content"]
    logger.info("LLM classification result: %s", result)
    return result

if __name__ == "__main__":
    sample_text = "Dear valued customer, your bank account requires immediate verification."
    result = classify_mail(sample_text)
    print("Classification:", result)
