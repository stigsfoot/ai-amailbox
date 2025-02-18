from fastapi import FastAPI, HTTPException
from fetch_emails import fetch_usps_email
from process_images import extract_text_from_image
from classify_mail import categorize_mail
from pathlib import Path
from typing import Dict, Any
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/check-mail")
async def check_mail() -> Dict[str, Any]:
    try:
        # Fetch emails asynchronously
        email_result = await fetch_usps_email()
        
        # Validate image path
        image_path = Path("./mail_images/example.jpg")
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Mail image not found")
        
        # Process image
        image_text = extract_text_from_image(str(image_path))
        if not image_text:
            raise HTTPException(status_code=422, detail="Failed to extract text from image")
        
        # Categorize mail
        category = categorize_mail(image_text)
        
        return {
            "status": "success",
            "category": category,
            "text_extracted": bool(image_text),
            "processed_image": str(image_path)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing mail: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
