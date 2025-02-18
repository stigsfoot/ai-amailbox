from fastapi import FastAPI, HTTPException
from fetch_emails import authenticate_gmail, fetch_usps_email
from process_images import extract_text_from_image
from classify_mail import classify_mail
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/check-mail")
def check_mail():
    # Authenticate and fetch mail images
    service = authenticate_gmail()
    images = fetch_usps_email(service)
    if not images:
        raise HTTPException(status_code=404, detail="No mail images found")
    
    # For this POC, process only the first image
    image_path = images[0]
    if not Path(image_path).exists():
        raise HTTPException(status_code=404, detail="Mail image not found")
    
    # Extract text from image
    text = extract_text_from_image(image_path)
    if not text:
        raise HTTPException(status_code=422, detail="Failed to extract text from image")
    
    # Classify mail text
    category = classify_mail(text)
    logger.info("Mail classified as: %s", category)
    
    return {
        "status": "success",
        "category": category,
        "extracted_text": text,
        "image": image_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)