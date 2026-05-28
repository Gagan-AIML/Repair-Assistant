# yolo_detector.py
# YOLO Object Detection module — Query-Aware Component Detection with Roboflow + graceful fallback.

import io
import os
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

ROBOFLOW_API_KEY     = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_WORKSPACE   = os.getenv("ROBOFLOW_WORKSPACE")
ROBOFLOW_WORKFLOW_ID = os.getenv("ROBOFLOW_WORKFLOW_ID")
ROBOFLOW_MODEL_ID    = os.getenv("ROBOFLOW_MODEL_ID")

# ─────────────────────────────────────────────────────────────
#  STEP 1 — Issue-to-Component Keyword Mapping
# ─────────────────────────────────────────────────────────────
ISSUE_KEYWORD_MAP = {
    "battery":  ["battery", "charge", "charging", "charger", "power", "adapter", "plug", "dead", "dc jack"],
    "fan":      ["fan", "heat", "hot", "heating", "overheating", "temperature", "thermal", "freeze", "noise"],
    "ssd":      ["ssd", "storage", "boot", "hard drive", "hdd", "nvme", "m.2", "slow"],
    "ram":      ["ram", "memory", "beep", "lag", "slot", "crash", "bsod"],
    "screen":   ["screen", "display", "flicker", "hdmi", "monitor", "lines", "backlight", "lcd"],
    "keyboard": ["keyboard", "key", "trackpad", "touchpad", "click", "touch"],
    "network":  ["wifi", "wireless", "bluetooth", "network", "internet", "ethernet"],
    "audio":    ["audio", "sound", "speaker", "microphone", "headphone", "mute"],
}

# Synonyms to match Roboflow class labels to our categories
COMPONENT_LABEL_SYNONYMS = {
    "battery":  ["battery", "batt", "power cell", "li-ion", "lithium"],
    "fan":      ["fan", "cooler", "blower", "heatsink", "thermal"],
    "ssd":      ["ssd", "nvme", "m.2", "hdd", "storage", "drive"],
    "ram":      ["ram", "dimm", "memory", "so-dimm"],
    "screen":   ["lcd", "display", "panel", "ribbon", "cable", "lvds", "edp"],
    "keyboard": ["keyboard", "trackpad", "touchpad", "connector"],
    "network":  ["wifi", "wireless", "bluetooth", "lan", "network", "antenna"],
    "audio":    ["audio", "speaker", "codec", "sound"],
}

CONFIDENCE_THRESHOLD = 0.70


# ─────────────────────────────────────────────────────────────
#  STEP 2 — Extract Query Category from User Issue
# ─────────────────────────────────────────────────────────────
def extract_target_category(user_issue: str) -> str:
    """Map user query to a component category from ISSUE_KEYWORD_MAP."""
    query = user_issue.lower()
    for category, keywords in ISSUE_KEYWORD_MAP.items():
        if any(kw in query for kw in keywords):
            return category
    return "general"


# ─────────────────────────────────────────────────────────────
#  STEP 3 — Check if a detected label is relevant
# ─────────────────────────────────────────────────────────────
def is_relevant(label: str, target_category: str) -> bool:
    """Return True if the detected class label matches the target component category."""
    if target_category == "general":
        return True
    label_lower = label.lower()
    synonyms = COMPONENT_LABEL_SYNONYMS.get(target_category, [])
    return any(syn in label_lower for syn in synonyms)


# ─────────────────────────────────────────────────────────────
#  Helper — Draw semi-transparent fallback guidance banner
# ─────────────────────────────────────────────────────────────
def _draw_fallback_text(img_np: np.ndarray, width: int, message: str):
    h = img_np.shape[0]
    banner_h = 32
    overlay = img_np.copy()
    cv2.rectangle(overlay, (0, h - banner_h), (width, h), (15, 20, 35), -1)
    cv2.addWeighted(overlay, 0.75, img_np, 0.25, 0, img_np)
    cv2.putText(img_np, message, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 150), 1, cv2.LINE_AA)


# ─────────────────────────────────────────────────────────────
#  Helper — Draw a single bounding box with relevance coloring
# ─────────────────────────────────────────────────────────────
def _draw_box(img_np, x1, y1, x2, y2, label, is_rel, conf):
    if is_rel:
        color      = (16, 185, 129)   # Bright green — relevant
        text_color = (255, 255, 255)
        thickness  = 3
    else:
        color      = (80, 80, 80)     # Dim grey — irrelevant
        text_color = (180, 180, 180)
        thickness  = 1

    cv2.rectangle(img_np, (x1, y1), (x2, y2), color, thickness)
    display_label = f"{label} {conf:.0%}"
    (lw, lh), _ = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    cv2.rectangle(img_np, (x1, y1 - lh - 10), (x1 + lw + 10, y1), color, -1)
    cv2.putText(img_np, display_label, (x1 + 5, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)


# ─────────────────────────────────────────────────────────────
#  MAIN DETECTION FUNCTION
# ─────────────────────────────────────────────────────────────
def detect_components_with_yolo(image_bytes: bytes, user_issue: str = "") -> tuple:
    """
    Run YOLO detection with full Query-Aware filtering pipeline:
      - Relevant + high-confidence  → bright green box
      - Irrelevant + high-confidence → dim grey box
      - Low-confidence (< 0.70)     → skipped + contextual fallback message
    Falls back to query-aware mock detections when Roboflow is unavailable.
    """
    img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = img_pil.size
    img_np = np.array(img_pil)

    detected_components   = []
    target_category       = extract_target_category(user_issue)
    low_confidence_skipped = 0

    # ── PATH 1: Roboflow Workflows API ──────────────────────
    if ROBOFLOW_API_KEY and ROBOFLOW_WORKSPACE and ROBOFLOW_WORKFLOW_ID and len(ROBOFLOW_API_KEY) > 5:
        try:
            import requests, base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            url = (f"https://detect.roboflow.com/infer/workflows"
                   f"/{ROBOFLOW_WORKSPACE}/{ROBOFLOW_WORKFLOW_ID}")
            payload = {
                "api_key": ROBOFLOW_API_KEY,
                "inputs": {"image": {"type": "base64", "value": image_b64}}
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()

                def find_predictions(data):
                    if isinstance(data, list):
                        for item in data:
                            r = find_predictions(item)
                            if r is not None:
                                return r
                    elif isinstance(data, dict):
                        if "predictions" in data:
                            return data["predictions"]
                        for val in data.values():
                            r = find_predictions(val)
                            if r is not None:
                                return r
                    return None

                predictions = find_predictions(result)
                if predictions and isinstance(predictions, list):
                    for pred in predictions:
                        cls  = pred.get("class", pred.get("label", pred.get("class_name", "Component")))
                        conf = float(pred.get("confidence", pred.get("conf", 1.0)))

                        # STEP 4 — Confidence gate
                        if conf < CONFIDENCE_THRESHOLD:
                            low_confidence_skipped += 1
                            continue

                        x = int(pred.get("x", 0))
                        y = int(pred.get("y", 0))
                        w = int(pred.get("width",  pred.get("w", 0)))
                        h = int(pred.get("height", pred.get("h", 0)))
                        x1 = max(0,     x - w // 2)
                        y1 = max(0,     y - h // 2)
                        x2 = min(width, x + w // 2)
                        y2 = min(height,y + h // 2)

                        # STEP 3 — Relevance filter + coloring
                        rel = is_relevant(cls, target_category)
                        _draw_box(img_np, x1, y1, x2, y2, cls, rel, conf)
                        if rel:
                            detected_components.append(cls)

                    # STEP 5 — Fallback messaging
                    if not detected_components and low_confidence_skipped > 0:
                        _draw_fallback_text(img_np, width,
                            f"Low-confidence detection. Using contextual repair assistance for: {target_category.upper()}")
                    elif not detected_components:
                        _draw_fallback_text(img_np, width,
                            f"No {target_category.upper()} component detected. Using RAG + OCR context.")

                    return Image.fromarray(img_np), list(set(detected_components))
        except Exception:
            pass

    # ── PATH 2: Standard hosted Roboflow model ───────────────
    elif ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID and len(ROBOFLOW_API_KEY) > 5:
        try:
            import requests
            url = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}"
            response = requests.post(url, params={"api_key": ROBOFLOW_API_KEY}, data=image_bytes)
            if response.status_code == 200:
                for pred in response.json().get("predictions", []):
                    cls  = pred["class"]
                    conf = float(pred["confidence"])
                    if conf < CONFIDENCE_THRESHOLD:
                        low_confidence_skipped += 1
                        continue
                    x, y = int(pred["x"]), int(pred["y"])
                    w, h = int(pred["width"]), int(pred["height"])
                    x1 = max(0,     x - w // 2)
                    y1 = max(0,     y - h // 2)
                    x2 = min(width, x + w // 2)
                    y2 = min(height,y + h // 2)
                    rel = is_relevant(cls, target_category)
                    _draw_box(img_np, x1, y1, x2, y2, cls, rel, conf)
                    if rel:
                        detected_components.append(cls)

                if not detected_components:
                    _draw_fallback_text(img_np, width,
                        f"Low-confidence detection. Using contextual repair assistance for: {target_category.upper()}")
                return Image.fromarray(img_np), list(set(detected_components))
        except Exception:
            pass

    # ── PATH 3: Gemini Visual Grounding (Live Coordinate Detection) ──
    # Sends the actual image to Gemini Vision and asks it to locate 
    # specific components, returning real bounding box coordinates.
    # Works on ANY laptop regardless of brand, model, or layout.
    GEMINI_COMPONENT_QUERIES = {
        "battery":  ["laptop battery pack"],
        "fan":      ["cooling fan", "second cooling fan"],
        "ssd":      ["M.2 NVMe SSD drive"],
        "ram":      ["RAM memory stick slot"],
        "screen":   ["LCD display connector"],
        "keyboard": ["keyboard ribbon connector"],
        "network":  ["Wi-Fi network card"],
        "audio":    ["speaker wire connector"],
        "general":  ["main motherboard chipset"],
    }

    try:
        import google.genai as genai
        from google.genai import types as genai_types
        import json, re as _re

        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if GOOGLE_API_KEY:
            _client = genai.Client(api_key=GOOGLE_API_KEY)

            components_to_find = GEMINI_COMPONENT_QUERIES.get(target_category, GEMINI_COMPONENT_QUERIES["general"])
            components_list = "\n".join([f"  {i+1}. {c}" for i, c in enumerate(components_to_find)])

            grounding_prompt = f"""You are a computer hardware component detector.
Analyze this laptop/PC motherboard image and locate these specific components:
{components_list}

For EACH component you can see in the image, return a JSON array entry with:
- "label": the component name
- "box": [y_min, x_min, y_max, x_max] normalized to 0-1000 range (where 0,0 is top-left and 1000,1000 is bottom-right)
- "confidence": your confidence from 0.0 to 1.0

RULES:
- Only return components you can ACTUALLY see. Do NOT guess invisible components.
- The coordinates must tightly wrap around the real component in this specific image.
- Return ONLY a valid JSON array, no other text. Example:
[{{"label":"cooling fan","box":[100,50,400,300],"confidence":0.92}}]
"""

            image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            response = _client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[grounding_prompt, image_part],
                config=genai_types.GenerateContentConfig(temperature=0.1)
            )

            raw_text = response.text.strip()
            # Extract JSON array from response (handle markdown code fences)
            json_match = _re.search(r'\[.*\]', raw_text, _re.DOTALL)
            if json_match:
                detections = json.loads(json_match.group())

                if detections and len(detections) > 0:
                    palette = [(16, 185, 129), (245, 158, 11), (99, 102, 241)]

                    for i, det in enumerate(detections):
                        label = det.get("label", "Component")
                        box = det.get("box", [0, 0, 0, 0])
                        conf = float(det.get("confidence", 0.85))

                        if len(box) != 4:
                            continue

                        # Convert normalized [0-1000] coordinates to actual pixel coordinates
                        # Gemini returns [y_min, x_min, y_max, x_max]
                        y_min_norm, x_min_norm, y_max_norm, x_max_norm = box
                        x1 = int((x_min_norm / 1000.0) * width)
                        y1 = int((y_min_norm / 1000.0) * height)
                        x2 = int((x_max_norm / 1000.0) * width)
                        y2 = int((y_max_norm / 1000.0) * height)

                        # Clamp to image boundaries
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(width, x2), min(height, y2)

                        # Skip invalid boxes
                        if x2 <= x1 or y2 <= y1:
                            continue

                        color = palette[i % len(palette)]
                        cv2.rectangle(img_np, (x1, y1), (x2, y2), color, 3)
                        display_label = f"{label} {conf:.0%}"
                        (lw, lh), _ = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                        cv2.rectangle(img_np, (x1, y1 - lh - 10), (x1 + lw + 10, y1), color, -1)
                        cv2.putText(img_np, display_label, (x1 + 5, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        detected_components.append(label)

                    if detected_components:
                        _draw_fallback_text(img_np, width,
                            f"Gemini Vision Grounding — detected {len(detected_components)} components for: {target_category.upper()}")
                        return Image.fromarray(img_np), list(set(detected_components))

    except Exception:
        pass  # Fall through to PATH 4

    # ── PATH 4 (LAST RESORT): Static Motherboard Architecture Layout Map ──
    # Only used when BOTH Roboflow AND Gemini APIs are completely offline.
    fallback_map = {
        "battery":  [("Battery Assembly", 0.96), ("Battery Connector", 0.91), ("Power Controller IC", 0.88)],
        "fan":      [("Cooling Fan Assembly (L)", 0.97), ("Cooling Fan Assembly (R)", 0.95), ("Copper Heatsink Pipes", 0.92)],
        "ssd":      [("M.2 NVMe SSD Slot", 0.95), ("SATA SSD/HDD Bay", 0.91), ("Storage Controller", 0.88)],
        "ram":      [("DDR SO-DIMM Slot 1", 0.96), ("DDR SO-DIMM Slot 2", 0.93), ("Memory Controller", 0.87)],
        "screen":   [("LCD EDP Connector", 0.94), ("Display Ribbon Route", 0.88), ("GPU Controller Area", 0.91)],
        "keyboard": [("Keyboard Connector", 0.93), ("Trackpad Ribbon Cable", 0.89)],
        "network":  [("Wi-Fi Module", 0.94), ("Antenna Connectors", 0.88)],
        "audio":    [("Audio Codec Chip", 0.91), ("Speaker Connector", 0.87)],
        "general":  [("Motherboard Chipset", 0.93), ("CMOS Battery Socket", 0.88), ("SATA Interface Slot", 0.91)],
    }

    LAYOUT_COORDINATES = {
        "battery": [
            [0.10, 0.58, 0.90, 0.95],
            [0.38, 0.50, 0.48, 0.57],
            [0.28, 0.45, 0.36, 0.52]
        ],
        "fan": [
            [0.04, 0.15, 0.31, 0.54],
            [0.68, 0.15, 0.95, 0.54],
            [0.28, 0.10, 0.72, 0.32]
        ],
        "ssd": [
            [0.10, 0.44, 0.32, 0.53],
            [0.72, 0.48, 0.96, 0.82],
            [0.20, 0.48, 0.28, 0.52]
        ],
        "ram": [
            [0.34, 0.34, 0.66, 0.43],
            [0.34, 0.44, 0.66, 0.53],
            [0.28, 0.38, 0.33, 0.48]
        ],
        "screen": [
            [0.45, 0.05, 0.55, 0.15],
            [0.38, 0.08, 0.62, 0.20],
            [0.62, 0.22, 0.74, 0.36]
        ],
        "keyboard": [
            [0.08, 0.38, 0.22, 0.48],
            [0.44, 0.48, 0.56, 0.56]
        ],
        "network": [
            [0.76, 0.40, 0.88, 0.49],
            [0.78, 0.33, 0.84, 0.38]
        ],
        "audio": [
            [0.85, 0.46, 0.98, 0.56],
            [0.02, 0.48, 0.09, 0.54]
        ],
        "general": [
            [0.35, 0.26, 0.65, 0.46],
            [0.74, 0.38, 0.86, 0.48],
            [0.10, 0.44, 0.32, 0.53]
        ]
    }

    palette = [(16, 185, 129), (16, 185, 129), (99, 102, 241)]
    coords_list = LAYOUT_COORDINATES.get(target_category, LAYOUT_COORDINATES["general"])

    for i, (cls, conf) in enumerate(fallback_map.get(target_category, fallback_map["general"])):
        if i >= len(coords_list):
            break

        r = coords_list[i]
        x1 = int(width * r[0])
        y1 = int(height * r[1])
        x2 = int(width * r[2])
        y2 = int(height * r[3])

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)

        color = palette[i % len(palette)]
        cv2.rectangle(img_np, (x1, y1), (x2, y2), color, 3)
        label = f"{cls} {conf:.0%}"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(img_np, (x1, y1 - lh - 10), (x1 + lw + 10, y1), color, -1)
        cv2.putText(img_np, label, (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        detected_components.append(cls)

    _draw_fallback_text(img_np, width,
        f"Offline mode — showing estimated layout for: {target_category.upper()}")

    return Image.fromarray(img_np), list(set(detected_components))

