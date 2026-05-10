import os
import io
import time
from collections import defaultdict, deque

import torch
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from transformers import AutoTokenizer, ViTImageProcessor, VisionEncoderDecoderModel

load_dotenv()

app = FastAPI(
    title="Smart Image Captioning API",
    description="An AI-powered API that automatically generates alt text for images to enhance web accessibility (a11y).",
)


RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

request_logs = defaultdict(deque)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


def check_rate_limit(request: Request) -> None:
    if not RATE_LIMIT_ENABLED:
        return

    client_ip = get_client_ip(request)
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    logs = request_logs[client_ip]

    while logs and logs[0] < window_start:
        logs.popleft()

    if len(logs) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Too many requests. Limit is "
                f"{RATE_LIMIT_REQUESTS} requests per "
                f"{RATE_LIMIT_WINDOW_SECONDS} seconds."
            ),
        )

    logs.append(now)


allowed_origins_env = os.getenv("ALLOWED_ORIGINS")

if allowed_origins_env:
    origins = [
        origin.strip()
        for origin in allowed_origins_env.split(",")
        if origin.strip()
    ]
else:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    print("\n" + "=" * 70)
    print("[CORS] ALLOWED_ORIGINS is not set.")
    print("[CORS] Using default local development origins:")
    for origin in origins:
        print(f"       - {origin}")
    print("=" * 70 + "\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


MODEL_NAME = "nlpconnect/vit-gpt2-image-captioning"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[System] Initializing on device: {device.type.upper()}")

print("[Info] Downloading and loading the AI model... This may take a while on the first run.")
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME).to(device)
feature_extractor = ViTImageProcessor.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("[Success] AI model loaded successfully!")

gen_kwargs = {
    "max_length": 16,
    "num_beams": 4,
}


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Smart Image Captioning API is running.",
        "rateLimitEnabled": RATE_LIMIT_ENABLED,
        "rateLimitRequests": RATE_LIMIT_REQUESTS,
        "rateLimitWindowSeconds": RATE_LIMIT_WINDOW_SECONDS,
        "maxFileSizeMB": MAX_FILE_SIZE_MB,
    }


@app.post("/api/generate-caption")
async def generate_caption(request: Request, file: UploadFile = File(...)):
    try:
        check_rate_limit(request)

        if file.content_type not in ALLOWED_IMAGE_TYPES:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Unsupported file type. Please upload a JPG, PNG, or WebP image.",
                },
            )

        image_bytes = await file.read()

        if len(image_bytes) > MAX_FILE_SIZE_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "status": "error",
                    "message": f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.",
                },
            )

        try:
            image = Image.open(io.BytesIO(image_bytes))
        except UnidentifiedImageError:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid image file.",
                },
            )

        if image.mode != "RGB":
            image = image.convert(mode="RGB")

        pixel_values = feature_extractor(
            images=image,
            return_tensors="pt",
        ).pixel_values.to(device)

        output_ids = model.generate(pixel_values, **gen_kwargs)
        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        caption = preds[0].strip()

        return JSONResponse(
            content={
                "status": "success",
                "caption": caption,
            },
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": "error",
                "message": e.detail,
            },
        )

    except Exception as e:
        print(f"[Error] Caption generation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Internal server error: {str(e)}",
            },
        )
