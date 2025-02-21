

# LetterLens POC

A proof-of-concept project that uses AI agents to analyze mail text and images using the Google Gemini API (via LiteLLM) and the smolagents framework, aiming to develop a new Generative UI approach for the frontend.

## Overview

- **Mail Text Analysis**: Extracts key details (sender, recipient) from mail text.
- **Mail Image Analysis**: Processes mail images (base64 encoded) to extract details.
- **FastAPI Endpoint**: Provides an API to check mail and return classification results.
- **Agent Orchestration**: Utilizes a CodeAgent to sequentially call the above tools.

## Motivation/Need

Traditional methods of managing physical mail are time-consuming and often inefficient. With the rise of AI and multi-agent systems, there's an opportunity to automate the extraction and classification of mail content. This project hypothesizes that a multi-agent approach can effectively handle the complexities of both text and image data in mail, leading to improved efficiency and accuracy in mail processing.

## Practicality

Implementing a multi-agent system allows for specialized agents to handle distinct tasks—such as text extraction, image processing, and data classification—working collaboratively to achieve a cohesive outcome. This modular design enhances scalability and maintainability, making it practical for real-world applications where mail volumes and types can vary significantly.

## Privacy Considerations

Handling sensitive mail content necessitates stringent privacy measures. The system ensures that all data processing occurs locally, minimizing exposure to external entities. Personal Identifiable Information (PII) is anonymized or redacted where possible, and data retention policies are enforced to prevent unnecessary storage of sensitive information. Compliance with data protection regulations, such as GDPR, is a foundational aspect of the project's design.

## Lessons Learned

Throughout the development of this POC, several key insights emerged:

- **Multi-Agent Coordination**: Effective communication between agents is crucial. Establishing clear protocols and data formats ensures seamless interaction and reduces errors.
- **Data Privacy Challenges**: Balancing functionality with privacy requires continuous assessment. Implementing robust encryption and access controls is essential to protect sensitive information.
- **Scalability Considerations**: As the system grows, optimizing agent performance and managing computational resources become critical to maintain efficiency.
- **User Feedback Integration**: Incorporating user feedback loops enhances system accuracy and user satisfaction, highlighting the importance of a human-centered design approach.

These lessons underscore the importance of thoughtful system architecture, proactive privacy measures, and iterative development informed by user experiences.


## Prerequisites

* Python 3.11.x
* [uv](https://github.com/astral-sh/uv) (a utility tool for managing virtual environments)
* Git


## Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/stigsfoot/ai-amailbox.git
cd backend
```

### 2. Create and Activate the Virtual Environment Using uv

In PowerShell, run:


```
uv venv .venv; .\.venv\Scripts\Activate.ps1
```


If you encounter an execution policy error, temporarily bypass it:


```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### **3. Install Dependencies**

You can manage dependencies using a modern configuration file. For example, using a `pyproject.toml`:


```
name = "mail-classification-poc"
version = "0.1.0"
dependencies = [
    "litellm",
    "smolagents",
    "python-dotenv",
    "fastapi",
    "uvicorn",
    "google-api-python-client"
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

```


Then install dependencies:


```
pip install -e .
```


Alternatively, if you use a lock file:


```
uv pip install litellm smolagents python-dotenv fastapi uvicorn google-api-python-client
uv pip freeze > requirements.lock
```

### **4. Configure Environment Variables**

Create a `.env` file in the project root with:


```
LITELLM_API_KEY=your-api-key
LITELLM_MODEL=gemini-1.5-pro
LITELLM_PROVIDER=google/ai-studio
```


Replace `your-api-key` with your actual API key.


## **Running the Application**


### **FastAPI Server**

To start the API server, run:


```
uvicorn main:app --reload
```


Then access the endpoint at: \
`http://127.0.0.1:8000/check-mail`



## **License**

TBD
