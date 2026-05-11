---
title: react-a11y-auto-caption-server
emoji: 🖼️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# react-a11y-auto-caption-server

Local AI caption server for `react-a11y-auto-caption`.

Run a FastAPI image-captioning server with one command:

```bash
npx react-a11y-auto-caption-server
```

This server uses the ViT-GPT2 image captioning model to generate alt text for images.

---

## Features

- Run the server with `npx`
- Automatic Python environment setup
- Local-first image captioning
- Works with `react-a11y-auto-caption`
- Uses GPU if available, otherwise falls back to CPU

---

## Requirements

- Node.js 18+
- Python 3.8+
- pip

Check your environment:

```bash
node --version
python --version
pip --version
```

---

## Quick Start

```bash
npx react-a11y-auto-caption-server
```

The server starts at:

```txt
http://127.0.0.1:8000
```

Caption endpoint:

```txt
http://127.0.0.1:8000/api/generate-caption
```

---

## First Run Notice

The first run may take a few minutes.

The CLI will:

- create a Python virtual environment
- install Python dependencies
- start the FastAPI server

The AI model may also be downloaded on the first caption request.  
After the first setup, future runs should be faster.

---

## Usage with React

Install the React package:

```bash
npm install react-a11y-auto-caption
```

Start the local server:

```bash
npx react-a11y-auto-caption-server
```

Use it in your app:

```tsx
import { SmartImage } from "react-a11y-auto-caption";

export default function Example() {
  return (
    <SmartImage
      src="/example.jpg"
      apiEndpoint="http://127.0.0.1:8000/api/generate-caption"
    />
  );
}
```

---

## API

### `POST /api/generate-caption`

Request:

- `Content-Type: multipart/form-data`
- Body field: `file`

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/generate-caption" \
  -F "file=@/path/to/image.jpg"
```

Response:

```json
{
  "status": "success",
  "caption": "a dog running through a grassy field"
}
```

---

## Manual Development

```bash
git clone https://github.com/kong33/SmartImage.git
cd SmartImage

python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

For macOS/Linux:

```bash
source venv/bin/activate
```

---

## Environment

If you use CORS settings, create a `.env` file:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Do not commit `.env`.

---

## Related

- `react-a11y-auto-caption`

---

## License

MIT
