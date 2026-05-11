import os
import io

import torch
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from transformers import AutoTokenizer, ViTImageProcessor, VisionEncoderDecoderModel

load_dotenv()

app = FastAPI(
    title="Smart Image Captioning API",
    description="An AI-powered API that automatically generates alt text for images to enhance web accessibility.",
)


allowed_origins_env = os.getenv("ALLOWED_ORIGINS")

if allowed_origins_env:
    origins = [
        origin.strip()
        for origin in allowed_origins_env.split(",")
        if origin.strip()
    ]
    allow_origin_regex = None

    print("\n" + "=" * 70)
    print("[CORS] Using ALLOWED_ORIGINS from environment:")
    for origin in origins:
        print(f"       - {origin}")
    print("=" * 70 + "\n")

else:
    origins = []
    allow_origin_regex = r"^https?://(localhost|127\.0\.0\.1):\d+$"

    print("\n" + "=" * 70)
    print("[CORS] ALLOWED_ORIGINS is not set.")
    print("[CORS] Allowing local development origins:")
    print("       - http://localhost:<any-port>")
    print("       - http://127.0.0.1:<any-port>")
    print("=" * 70 + "\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
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
        "endpoint": "/api/generate-caption",
    }


@app.post("/api/generate-caption")
async def generate_caption(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

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

    except Exception as e:
        print(f"[Error] Caption generation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Internal server error: {str(e)}",
            },
        )