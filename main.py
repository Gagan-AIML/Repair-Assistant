import os
import io
import concurrent.futures
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import base64
from dotenv import load_dotenv

load_dotenv(override=True)

import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.engines.yolo_detector import detect_components_with_yolo
from backend.engines.ocr_extractor import extract_ocr_context_with_gemini
from backend.engines.rag_engine import load_vectorstore, run_rag_diagnosis

app = FastAPI(title="RepairAI Backend API")

# Allow CORS for React frontend (development and production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load vectorstore on startup
try:
    vectorstore = load_vectorstore()
    print("Vectorstore loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load vectorstore initially. {e}")
    vectorstore = None

def run_vision_analysis(image_bytes, user_issue):
    import google.genai as genai
    from google.genai import types as genai_types
    from dotenv import load_dotenv
    
    load_dotenv(override=True)
    fresh_key = os.getenv("GOOGLE_API_KEY")
    if not fresh_key:
        return "Vision damage analysis unavailable: GOOGLE_API_KEY not configured."

    client = genai.Client(api_key=fresh_key)
    
    vision_prompt = f"""
    You are an expert electronics repair technician.
    The user reported: "{user_issue}"
    Analyze this image and identify visual defects: burns, swollen caps, cracks, corrosion, dust blockages, or loose connectors.
    Be specific about component locations and severity.
    """
    try:
        image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[vision_prompt, image_part]
        )
        return response.text
    except Exception as e:
        return f"Vision damage analysis failed: {e}"

# Mount static files
app.mount("/static", StaticFiles(directory="frontend_web"), name="static")

@app.get("/")
def read_root():
    return FileResponse("frontend_web/index.html")

@app.post("/api/diagnose")
async def diagnose(user_issue: str = Form(...), image: UploadFile = File(None)):
    if not user_issue.strip():
        raise HTTPException(status_code=400, detail="User issue description is required.")

    global vectorstore
    if vectorstore is None:
        try:
            vectorstore = load_vectorstore()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not load knowledge base: {e}")

    image_bytes = None
    if image:
        image_bytes = await image.read()

    annotated_img_base64 = None
    detected_components = []
    ocr_context = ""
    vision_analysis = ""

    if image_bytes:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_yolo = executor.submit(detect_components_with_yolo, image_bytes, user_issue)
            future_ocr = executor.submit(extract_ocr_context_with_gemini, image_bytes)
            future_vision = executor.submit(run_vision_analysis, image_bytes, user_issue)

            try:
                annotated_pil, detected_components = future_yolo.result(timeout=30)
                # Convert PIL Image → JPEG bytes → base64 string for JSON transport
                if annotated_pil is not None:
                    buf = io.BytesIO()
                    annotated_pil.save(buf, format="JPEG", quality=85)
                    buf.seek(0)
                    annotated_img_base64 = f"data:image/jpeg;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
            except Exception as e:
                print(f"YOLO error: {e}")
                annotated_img_base64 = None
                detected_components = []

            try:
                ocr_context = future_ocr.result(timeout=20)
            except Exception as e:
                print(f"OCR error: {e}")
                ocr_context = "OCR Extraction unavailable."

            try:
                vision_analysis = future_vision.result(timeout=20)
            except Exception as e:
                print(f"Vision error: {e}")
                vision_analysis = "Vision damage analysis unavailable."
    else:
        vision_analysis = "No image provided. Diagnosis based on text description only."
        ocr_context = "No image provided."
        detected_components = []

    try:
        sections = run_rag_diagnosis(user_issue, vision_analysis, detected_components, ocr_context, vectorstore)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis generation failed: {e}")

    # Determine verdict and device type
    verdict_text = sections.get("verdict", "")
    is_user_fix = "USER CAN FIX" in verdict_text or "✅" in verdict_text

    device_type = "Device"
    issue_lower = user_issue.lower()
    if any(k in issue_lower for k in ["phone", "mobile", "android", "iphone", "pixel"]):
        device_type = "Phone"
    elif any(k in issue_lower for k in ["desktop", "monitor", "pc", "computer", "motherboard", "graphics"]):
        device_type = "Computer"
    elif any(k in issue_lower for k in ["laptop", "notebook", "macbook", "thinkpad"]):
        device_type = "Laptop"

    return {
        "annotated_image": annotated_img_base64,
        "detected_components": detected_components,
        "ocr_context": ocr_context,
        "vision_analysis": vision_analysis,
        "sections": sections,
        "is_user_fix": is_user_fix,
        "device_type": device_type
    }


@app.post("/api/chat")
async def chat_followup(
    user_question: str = Form(...),
    original_issue: str = Form(default=""),
    causes: str = Form(default=""),
    fixes: str = Form(default=""),
    verdict: str = Form(default=""),
    tips: str = Form(default=""),
    vision_analysis: str = Form(default=""),
    ocr_context: str = Form(default=""),
    detected_components: str = Form(default=""),
    chat_history: str = Form(default="")
):
    """Follow-up chat endpoint. Takes a question + full diagnosis context and returns a focused AI answer."""
    load_dotenv(override=True)
    fresh_key = os.getenv("GOOGLE_API_KEY")
    if not fresh_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured.")

    import google.genai as genai
    from google.genai import types as genai_types

    client = genai.Client(api_key=fresh_key)

    prompt = f"""You are RepairAI, an expert device repair assistant. You already performed a full diagnosis for this user.

ORIGINAL USER ISSUE:
{original_issue}

PREVIOUS DIAGNOSIS RESULTS:
--- Possible Causes ---
{causes}

--- Recommended Fixes ---
{fixes}

--- Verdict ---
{verdict}

--- Prevention Tips ---
{tips}

--- Vision Analysis ---
{vision_analysis}

--- OCR Context ---
{ocr_context}

--- Detected Components ---
{detected_components}

PREVIOUS CONVERSATION:
{chat_history}

USER'S NEW FOLLOW-UP QUESTION:
{user_question}

Answer the follow-up question in a helpful, concise manner based on the diagnosis context above.
Be specific and actionable. Use markdown formatting with **bold** for key terms and numbered lists where appropriate.
Do NOT repeat the full diagnosis — just answer the specific question asked."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(temperature=0.4)
        )
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")
