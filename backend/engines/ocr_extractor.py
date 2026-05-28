# ocr_extractor.py
# High-fidelity OCR extraction using Gemini Vision to read motherboard serials and IC codes.

import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
import google.genai as genai
# pyrefly: ignore [missing-import]
from google.genai import types as genai_types


def extract_ocr_context_with_gemini(image_bytes: bytes) -> str:
    """Use Gemini Vision to extract technical printed texts, serial numbers, labels, or chip names from the image."""
    load_dotenv(override=True)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        return "OCR Extraction unavailable: GOOGLE_API_KEY not configured in .env"

    ocr_prompt = """
    Perform Optical Character Recognition (OCR) on this electronic component image.
    Extract and list all printed text, chip markings, serial numbers, motherboard codes, revision numbers, brand names (e.g. Realtek, Intel, Dell, Asus, Gigabyte), and connector labels (e.g. J1, FAN1, BAT1).
    Be extremely precise. If no clear text is legible, reply with 'No legible text found'.
    """
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[ocr_prompt, image_part]
        )
        return response.text.strip()
    except Exception as e:
        print(f"[OCR Error] Failed to run Gemini OCR: {e}")
        return f"OCR Extraction unavailable: {str(e)}"
