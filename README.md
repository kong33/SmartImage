# SmartImage AI Captioning API

> A lightweight, secure FastAPI microservice designed to power the `react-a11y-auto-caption` library. <br/>
It uses the ViT-GPT2 model to automatically generate highly accurate alt text for images, enhancing web accessibility (a11y).

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![AI Model](https://img.shields.io/badge/Model-ViT--GPT2-yellow.svg)](https://huggingface.co/nlpconnect/vit-gpt2-image-captioning)

## Features

- **Ready-to-Use:** Plug-and-play architecture for image captioning.
- **Secure by Default:** Strict CORS middleware configuration using environment variables.
- **Hardware Agnostic:** Automatically detects and runs on GPU (CUDA) if available, gracefully falling back to CPU.
- **Optimized for Frontend:** Returns clean, stripped captions ready for immediate UI injection.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- Git

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/kong33/SmartImage.git
cd SmartImage

# Create and activate a virtual environment
python -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
*(Note: If you are using a GPU, make sure to install the specific PyTorch version for your CUDA toolkit from the [official PyTorch website](https://pytorch.org/).)*

---

## Configuration (Security)

For security reasons, this server blocks all cross-origin requests by default.<br/>
You **MUST** create a `.env` file in the root directory to specify which frontends are allowed to communicate with this API.

Create a `.env` file:

```env
# Allow local React/Next.js development servers
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# For production, add your domain
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

---

## Running the Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> Note on First Run: The very first time you start the server or make an API request, the application will download the AI model (~1GB) from Hugging Face. This may take a few minutes depending on your internet connection. Subsequent runs will be instant.

---

## 📡 API Reference

### `POST /api/generate-caption`

Generates an accessibility caption for the uploaded image.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** `file` (The image file: jpg, png, etc.)

**cURL Example:**

```bash
curl -X POST "http://localhost:8000/api/generate-caption" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

**Successful Response (200 OK):**

```json
{
  "status": "success",
  "caption": "a dog running through a grassy field"
}
```

**Error Response (500 Internal Server Error):**

```json
{
  "status": "error",
  "message": "Internal server error: [detailed error message]"
}
```
