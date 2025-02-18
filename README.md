

# Letterlens POC

A proof-of-concept project that uses AI agents to analyze mail text and images using the Google Gemini AOI (via LiteLLM) and smolagents framework and eventually a new Generative UI approach for the frontend.


## Overview

* **Mail Text Analysis:** Extracts key details (sender, recipient) from mail text.
* **Mail Image Analysis:** Processes mail images (base64 encoded) to extract details.
* **FastAPI Endpoint:** Provides an API to check mail and return classification results.
* **Agent Orchestration:** Uses a CodeAgent to call the above tools sequentially.


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
