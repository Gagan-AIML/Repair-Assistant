# 🔧 AI AR Repair Assistant — Complete Project Capsule & Developer Handover Guide

> **Purpose**: This document is a comprehensive technical handover capsule. It contains everything a new developer (or an AI coding assistant) needs to understand, run, and extend this project.

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [System Architecture & Tech Stack](#2-system-architecture--tech-stack)
3. [Directory Structure & File-by-File Map](#3-directory-structure--file-by-file-map)
4. [Key Features Implemented](#4-key-features-implemented)
5. [How the AI Diagnosis Pipeline Works](#5-how-the-ai-diagnosis-pipeline-works)
6. [Installation & How to Run](#6-installation--how-to-run)
7. [Environment Variables (.env)](#7-environment-variables)
8. [Known Issues & Gotchas](#8-known-issues--gotchas)
9. [Future Roadmap & AI Prompts for Continuation](#9-future-roadmap--ai-prompts-for-continuation)

---

## 1. Project Overview

The **AI AR Repair Assistant** is an intelligent, multimodal hardware diagnostic and repair application. A user uploads (or captures live) a photo of a laptop/PC motherboard, describes their issue in plain English, and the system:

1. **Detects** the relevant hardware components on the image using computer vision (bounding boxes).
2. **Reads** printed text, chip markings, and serial numbers using OCR.
3. **Analyzes** the image for visual damage (burns, corrosion, swollen capacitors).
4. **Generates** a structured repair report with causes, step-by-step fixes, a verdict (user-fixable or service center), and preventive tips — all powered by a RAG (Retrieval-Augmented Generation) pipeline backed by a local vector database of repair manuals.

### Target Users
- Electronics repair technicians
- Engineering students learning hardware diagnostics
- DIY laptop repair hobbyists

---

## 2. System Architecture & Tech Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Streamlit)                     │
│  app.py ─── styles.py ─── formatters.py                        │
│  • Issue text input       • Dark cyberpunk CSS    • HTML cards  │
│  • Image upload / camera  • Animations            • Steppers   │
│  • Progress bar           • Responsive layout     • Verdicts   │
└────────────────────────────┬────────────────────────────────────┘
                             │ Internal Python calls (parallel)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (Python Engines)                    │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  yolo_detector.py │  │ ocr_extractor.py │  │ rag_engine.py │ │
│  │                   │  │                  │  │               │ │
│  │ Path 1: Roboflow  │  │ Gemini Vision    │  │ ChromaDB      │ │
│  │ Path 2: Roboflow  │  │ OCR extraction   │  │ vector search │ │
│  │ Path 3: Gemini    │  │ of chip text,    │  │ + Gemini LLM  │ │
│  │   Visual Grounding│  │ serial numbers,  │  │ structured    │ │
│  │ Path 4: Static    │  │ brand names      │  │ report gen    │ │
│  │   fallback coords │  │                  │  │               │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                 │
│  External APIs: Gemini 2.5 Flash, Roboflow Workflows            │
│  Local DB: ChromaDB with gemini-embedding-001 embeddings        │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | UI rendering, file upload, camera capture, progress bars |
| **LLM** | Gemini 2.5 Flash (`google-genai` SDK) | Vision analysis, OCR, RAG diagnosis generation |
| **Object Detection** | Roboflow API + Gemini Visual Grounding | Bounding box detection on motherboard images |
| **Vector Database** | ChromaDB + LangChain | Stores embedded repair guide chunks for semantic retrieval |
| **Embeddings** | `models/gemini-embedding-001` | Converts repair text into vector embeddings |
| **Concurrency** | Python `concurrent.futures.ThreadPoolExecutor` | Runs YOLO, OCR, and Vision Analysis in parallel |
| **Styling** | Custom inline CSS (cyberpunk dark theme) | Premium card-based visual design |

---

## 3. Directory Structure & File-by-File Map

```
AI-Repair-Assistant/
│
├── .env                          # API keys (GOOGLE_API_KEY, ROBOFLOW_*)
├── .env.example                  # Template showing required env vars
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── run.bat                       # Windows launch script (double-click)
├── README.md                     # Basic project readme
├── PROJECT_CAPSULE.md            # THIS FILE — full handover document
│
├── frontend/                     # ── UI Layer ──
│   ├── app.py                    # Main Streamlit application & orchestrator
│   ├── styles.py                 # CSS stylesheet (STYLE_CSS constant)
│   └── formatters.py             # HTML card formatters for diagnosis output
│
├── backend/                      # ── Processing Layer ──
│   ├── engines/
│   │   ├── yolo_detector.py      # Component detection (4-path fallback)
│   │   ├── ocr_extractor.py      # Gemini Vision OCR text extraction
│   │   └── rag_engine.py         # RAG retrieval + LLM diagnosis generator
│   │
│   └── database/
│       └── chroma_db/            # ChromaDB persistent vector store
│
├── chroma_db/                    # Alternative ChromaDB location (legacy)
│
└── .venv/                        # Python virtual environment
```

### Detailed File Descriptions

#### `frontend/app.py` — Main Application Entrypoint
- Sets up the Streamlit page config (title, icon, layout).
- Injects the CSS from `styles.py`.
- Renders two input columns: issue text area + image input (upload or camera).
- On "Run AI Diagnosis" click:
  - Loads the ChromaDB vector store.
  - Runs **3 parallel threads** (YOLO detection, OCR extraction, Vision damage analysis).
  - Passes all results to the RAG engine for structured report generation.
  - Renders the final diagnosis using HTML formatters.

#### `frontend/styles.py` — CSS Design System
- Contains a single `STYLE_CSS` string constant with all CSS rules.
- Dark cyberpunk theme (`#0B0F19` background, neon green accents `#10b981`).
- Includes card styles, button animations, progress bar themes, and responsive layout rules.

#### `frontend/formatters.py` — Output Card Generators
- `format_causes_html(text)` — Parses numbered causes into styled cards with numbers and descriptions.
- `format_fixes_html(text)` — Parses `### Fix N:` blocks into step-by-step procedural cards with difficulty badges (EASY/MEDIUM/HARD) and tool requirement banners.
- `format_verdict_html(text)` — Renders the "User Can Fix" or "Go to Service Center" verdict with color-coded styling.
- `format_tips_html(text)` — Renders preventive maintenance tips.
- `format_vision_analysis_html(text)` — Renders the AI vision damage analysis output.

#### `backend/engines/yolo_detector.py` — Component Detection Engine
- **ISSUE_KEYWORD_MAP**: Maps user query keywords (e.g., "hot", "fan", "charging") to component categories (e.g., `"fan"`, `"battery"`).
- **COMPONENT_LABEL_SYNONYMS**: Maps categories to detection label synonyms for relevance filtering.
- **`detect_components_with_yolo(image_bytes, user_issue)`**: Main function with 4 hierarchical detection paths:
  - **Path 1**: Roboflow Workflows API (if credentials configured).
  - **Path 2**: Roboflow Standard Model API (fallback).
  - **Path 3**: **Gemini Visual Grounding** — sends the actual image to Gemini Vision with a structured prompt asking it to locate specific components and return bounding box coordinates in `[y_min, x_min, y_max, x_max]` format normalized to 0–1000. These are converted to pixel coordinates and drawn on the image.
  - **Path 4**: Static relative coordinate fallback (hardcoded positions, last resort).
- **GEMINI_COMPONENT_QUERIES**: Dictionary mapping each category to the specific component names Gemini should look for. Currently trimmed to focus on primary components only (e.g., `"battery": ["laptop battery pack"]`).

#### `backend/engines/ocr_extractor.py` — OCR Text Extraction
- **`extract_ocr_context_with_gemini(image_bytes)`**: Sends the image to Gemini Vision with an OCR prompt asking it to extract all printed text, chip markings, serial numbers, revision codes, brand names, and connector labels.
- Dynamically loads the API key at call-time using `load_dotenv(override=True)`.
- Returns extracted text or a descriptive error message.

#### `backend/engines/rag_engine.py` — RAG Diagnosis Generator
- **`load_vectorstore(db_path)`**: Loads the ChromaDB vector database using LangChain's `Chroma` wrapper with `GoogleGenerativeAIEmbeddings`.
- **FALLBACK_DIAGNOSES**: Hardcoded offline fallback diagnoses for common categories (battery, fan, ssd, ram, general). Used when the Gemini API is unavailable (429/503 errors).
- **`run_rag_diagnosis(user_issue, vision_analysis, detected_components, ocr_context, vectorstore)`**:
  1. Builds a combined query from issue + components + OCR + vision analysis.
  2. Retrieves top-5 relevant document chunks from ChromaDB.
  3. Constructs a structured prompt asking Gemini to generate: POSSIBLE CAUSES, RECOMMENDED FIXES, VERDICT, and ADDITIONAL TIPS.
  4. Parses the response into sections using header-based splitting.
  5. Falls back to `FALLBACK_DIAGNOSES` if the API call fails.

#### `.env` — Environment Configuration
```ini
GOOGLE_API_KEY=<your_gemini_api_key>
ROBOFLOW_API_KEY=<your_roboflow_key>
ROBOFLOW_WORKSPACE=<your_workspace>
ROBOFLOW_WORKFLOW_ID=<your_workflow_id>
```

#### `requirements.txt` — Dependencies
```
streamlit
langchain
langchain-google-genai
langchain-chroma
chromadb
numpy
python-dotenv
google-generativeai
Pillow
google-genai
duckduckgo-search
inference-sdk
supervision
opencv-python-headless
requests
roboflow
```

---

## 4. Key Features Implemented

### A. Query-Aware Object Detection (4-Path Fallback)
The system maps the user's natural language issue to a hardware category, then uses that category to filter which components are detected and highlighted on the image. If Roboflow APIs are unavailable, it seamlessly falls back to Gemini Visual Grounding, which works on any laptop image regardless of brand or model.

### B. Gemini Visual Grounding (Path 3)
Sends the actual uploaded image to Gemini 2.5 Flash with a structured prompt requesting bounding box coordinates. Gemini returns JSON with `[y_min, x_min, y_max, x_max]` normalized to 0–1000, which is converted to pixel coordinates and drawn as colored rectangles with confidence labels.

### C. Parallel Vision Pipeline (3X Speed Boost)
YOLO detection, OCR extraction, and Vision damage analysis run concurrently using `ThreadPoolExecutor(max_workers=3)`. This reduced diagnosis time from ~15 seconds to ~4 seconds.

### D. Live Camera Capture
Users can toggle between "Upload Image File" and "Capture Live Photo" using a horizontal radio selector. The camera widget uses `st.camera_input` for native webcam access.

### E. Dynamic API Key Loading
All Gemini client instances are initialized at call-time using `load_dotenv(override=True)` and `genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))`. This prevents stale key caching issues in Streamlit's persistent module imports.

### F. Offline Fallback Diagnoses
If the Gemini API returns 429 (rate limit) or 503 (service unavailable), the system automatically falls back to pre-written, high-quality offline diagnoses for common categories (battery, fan, SSD, RAM, general).

### G. Structured Report Parsing
The LLM output is parsed into 4 sections using header-based splitting: POSSIBLE CAUSES, RECOMMENDED FIXES, VERDICT, and ADDITIONAL TIPS. Each section is rendered through dedicated HTML formatters with custom styling.

---

## 5. How the AI Diagnosis Pipeline Works

When a user clicks "Run AI Diagnosis", the following happens:

```
Step 1: Load ChromaDB vector store
            │
Step 2: Run 3 tasks IN PARALLEL ──────────────────────┐
            │                                          │
   ┌────────┴────────┐   ┌───────────────┐   ┌───────┴────────┐
   │ YOLO Detection  │   │ OCR Extraction│   │ Vision Damage  │
   │ (Roboflow or    │   │ (Gemini reads │   │ Analysis       │
   │  Gemini Visual  │   │  chip text)   │   │ (Gemini scans  │
   │  Grounding)     │   │               │   │  for defects)  │
   └────────┬────────┘   └───────┬───────┘   └───────┬────────┘
            │                    │                    │
            └──────────┬─────────┘                    │
                       │                              │
Step 3: Combine all results ◄─────────────────────────┘
            │
Step 4: Query ChromaDB for relevant repair guide chunks
            │
Step 5: Send combined context + retrieved docs to Gemini 2.5 Flash
            │
Step 6: Parse structured response into sections
            │
Step 7: Render beautiful HTML cards in Streamlit UI
```

---

## 6. Installation & How to Run

### Prerequisites
- Python 3.9 or higher
- pip package manager
- A valid Google Gemini API key (get one free at https://aistudio.google.com/apikey)

### Setup Steps

```powershell
# 1. Navigate to the project directory
cd "H:\My project\AI-Repair-Assistant"

# 2. Create and activate the virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Configure your API key
# Edit the .env file and paste your GOOGLE_API_KEY

# 5. Run the application
streamlit run frontend/app.py --server.port 8502
```

Or simply **double-click `run.bat`** to launch everything automatically.

The app will open at **http://localhost:8502**.

---

## 7. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | **Yes** | Your Google Gemini API key. Powers OCR, Vision Analysis, Visual Grounding, and RAG generation. |
| `ROBOFLOW_API_KEY` | Optional | Roboflow API key for YOLO Path 1 & 2. If empty, system uses Gemini Grounding (Path 3). |
| `ROBOFLOW_WORKSPACE` | Optional | Roboflow workspace name. |
| `ROBOFLOW_WORKFLOW_ID` | Optional | Roboflow workflow ID for the detection pipeline. |

---

## 8. Known Issues & Gotchas

1. **Gemini Rate Limits**: The free tier of Gemini 2.5 Flash has a limit of ~20 requests per minute. If you run multiple diagnoses rapidly, you may hit 429 errors. The system handles this gracefully with offline fallback diagnoses.

2. **ChromaDB Path**: The vector store can exist in either `backend/database/chroma_db/` or `chroma_db/` (root level). The `load_vectorstore()` function in `rag_engine.py` checks `backend/database/chroma_db/` by default. If your database is elsewhere, pass the path explicitly.

3. **Camera Permission**: The "Capture Live Photo" feature requires browser webcam permission. Streamlit will prompt for this automatically. On some browsers, HTTPS may be required for camera access.

4. **Large Images**: Very high-resolution images (>4000px) may slow down the Gemini Vision API. Consider resizing before upload if performance is an issue.

---

## 9. Future Roadmap & AI Prompts for Continuation

If you are continuing development on this project using an AI coding assistant, here are ready-to-use prompts for the next milestones:

### Milestone 1: Convert to HTML/CSS/JS + FastAPI
> *"I have a Streamlit-based AI repair assistant. The backend logic is in `backend/engines/` (yolo_detector.py, ocr_extractor.py, rag_engine.py). Help me create a FastAPI server in a new `main.py` with a single POST endpoint `/api/diagnose` that accepts an image file and a query string, runs the parallel detection/OCR/vision pipeline, and returns the structured diagnosis as JSON. Then help me build a premium dark-themed HTML/CSS/JS single-page frontend that communicates with this API using fetch()."*

### Milestone 2: Build Mobile App (Android APK)
> *"I have a web frontend (HTML/CSS/JS) and a deployed backend API. Help me use Capacitor to wrap my frontend into a native Android project so I can build an installable APK file. The app should point to my deployed API URL for processing."*

### Milestone 3: Real-Time AR Component Overlay
> *"In my HTML frontend, the backend returns bounding box coordinates as JSON `[y_min, x_min, y_max, x_max]` normalized to 0-1000. Help me use an HTML5 Canvas overlay on top of the uploaded image to draw animated, glowing bounding boxes at these coordinates with pulsing labels."*

### Milestone 4: Add More Repair Knowledge
> *"I have a ChromaDB vector store populated with repair guides. Help me write a script called `build_db.py` that reads PDF repair manuals from a `docs/` folder, splits them into chunks, embeds them using gemini-embedding-001, and stores them in ChromaDB for RAG retrieval."*

---

**End of Project Capsule.**
*Last updated: May 27, 2026*
