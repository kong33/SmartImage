from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

app = FastAPI(
    title="Smart Image Captioning API",
    description="AI가 이미지를 분석하여 접근성(a11y)을 위한 대체 텍스트(alt text)를 생성합니다."
)

MODEL_NAME = "nlpconnect/vit-gpt2-image-captioning"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"현재 사용 중인 장치: {device}")

print("AI 모델을 다운로드하고 메모리에 올리는 중입니다... (최초 1회 약 1GB 다운로드로 시간이 걸릴 수 있습니다.)")
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME).to(device)
feature_extractor = ViTImageProcessor.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("✅ AI 모델 로딩 완료!")

max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

@app.get("/")
async def root():
    return {"message": "AI Captioning API is running!"}

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


        return JSONResponse(content={"caption": caption, "status": "success"})
        
    except Exception as e:

        return JSONResponse(status_code=500, content={"message": str(e), "status": "error"})