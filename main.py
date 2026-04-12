import os
import io
import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Smart Image Captioning API",
    description="An AI-powered API that automatically generates alt text for images to enhance web accessibility (a11y)."
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")

if not allowed_origins_env:
    print("\n" + "="*70)
    print("[Security Warning] 'ALLOWED_ORIGINS' environment variable is missing!")
    print("All external CORS requests will be blocked by default.")
    print("Fix: Set your frontend URL in the environment variables or .env file.")
    print("Example: ALLOWED_ORIGINS=http://localhost:3000,https://my-app.com")
    print("="*70 + "\n")
    origins = []  
else:
    origins = allowed_origins_env.split(",")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "nlpconnect/vit-gpt2-image-captioning"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[System] Initializing on device: {device.type.upper()}")

print("[Info] Downloading and loading the AI model... (This may take a while on the first run)")
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME).to(device)
feature_extractor = ViTImageProcessor.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("✅ [Success] AI Model loaded successfully!")

# Generation configurations
gen_kwargs = {
    "max_length": 16, 
    "num_beams": 4
}

@app.get("/")
async def root():
    return {"message": "Smart Image Captioning API is running securely."}

@app.post("/api/generate-caption")
async def generate_caption(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        if image.mode != "RGB":
            image = image.convert(mode="RGB")

        pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        output_ids = model.generate(pixel_values, **gen_kwargs)
        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        caption = preds[0].strip()

        return JSONResponse(
            content={
                "status": "success",
                "caption": caption
            }
        )
        
    except Exception as e:
        print(f"[Error] Caption generation failed: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }
        )