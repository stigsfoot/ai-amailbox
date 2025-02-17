from smolai import Agent

# Email Retrieval Agent
email_agent = Agent(
    name="EmailFetcher",
    description="Fetches USPS Informed Delivery emails and extracts images.",
    instructions="Retrieve emails using Gmail API and extract image attachments."
)

# Image Processing Agent
image_agent = Agent(
    name="ImageProcessor",
    description="Extracts text from images using GPT-4o vision API.",
    instructions="Use OpenAI's GPT-4o or Gemini to extract text from mail images."
)

# Classification Agent
classification_agent = Agent(
    name="MailClassifier",
    description="Categorizes mail as important or spam.",
    instructions="Determine if mail is important based on sender, content, or recipient."
)