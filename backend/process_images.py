import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_image(image_path):
    with open(image_path, "rb") as image:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Extract the sender and recipient from this mail image."}],
            files={"image": image.read()},
        )
    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    text = extract_text_from_image("./mail_images/example.jpg")
    print(text)
