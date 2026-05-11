# react-a11y-auto-caption-server

Local AI caption server for [`react-a11y-auto-caption`](https://www.npmjs.com/package/react-a11y-auto-caption).

Run a FastAPI image-captioning server with one command:

```bash
npx react-a11y-auto-caption-server
```

This server uses the ViT-GPT2 image captioning model to generate alt text for images.

---

## Features

- Run the server with `npx`
- Automatic Python virtual environment setup
- Local-first image captioning
- Works with `react-a11y-auto-caption`
- Custom port support
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

On some systems, use:

```bash
python3 --version
pip3 --version
```

---

## Quick Start

```bash
npx react-a11y-auto-caption-server
```

Default server URL:

```txt
http://127.0.0.1:8000
```

Caption endpoint:

```txt
http://127.0.0.1:8000/api/generate-caption
```

---

## Custom Port

The default port is `8000`.

Use `--port` or `-p` to run the server on another port:

```bash
npx react-a11y-auto-caption-server --port 5000
```

or:

```bash
npx react-a11y-auto-caption-server -p 5000
```

Then use this endpoint in your frontend:

```txt
http://127.0.0.1:5000/api/generate-caption
```

Example:

```tsx
<SmartImage
  src="/example.jpg"
  apiEndpoint="http://127.0.0.1:5000/api/generate-caption"
/>
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

Start the local caption server:

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

## CORS

For local development, the server allows local frontend origins by default.

If `ALLOWED_ORIGINS` is not set, local origins such as these are allowed:

```txt
http://localhost:<any-port>
http://127.0.0.1:<any-port>
```

For production or internal company servers, set `ALLOWED_ORIGINS` manually.

Example:

```env
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
```

If your frontend runs on your laptop and the caption server runs on another machine, allow the frontend origin:

```env
ALLOWED_ORIGINS=http://localhost:3000
```

Then use the server machine address as the API endpoint:

```tsx
<SmartImage
  src="/example.jpg"
  apiEndpoint="http://192.168.0.20:8000/api/generate-caption"
/>
```

Do not commit your `.env` file.

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

Run on another port:

```bash
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

---

## Troubleshooting

### Port 8000 is unavailable

If port `8000` is already used or blocked, run the server on another port:

```bash
npx react-a11y-auto-caption-server --port 8001
```

Then update your frontend endpoint:

```tsx
<SmartImage
  src="/example.jpg"
  apiEndpoint="http://127.0.0.1:8001/api/generate-caption"
/>
```

### The API request does not run

Check that:

- `apiEndpoint` points to `/api/generate-caption`
- your frontend uses the same port as the server
- your image does not already have an `alt` value if you expect AI generation
- your frontend package is updated to the latest version

---

## Related

- [`react-a11y-auto-caption`](https://www.npmjs.com/package/react-a11y-auto-caption)

---

## License

MIT
