# 🔧 RepairAI — RAG-Based Device Repair Assistant

> An AI-powered repair assistant that analyzes your device issue and internal component photos to diagnose problems and guide you through fixing them.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green?style=flat-square)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-orange?style=flat-square&logo=google)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-purple?style=flat-square)

---

## 📌 What Is This Project?

RepairAI is a **multimodal RAG (Retrieval-Augmented Generation)** system for device repair diagnosis. Instead of giving generic AI answers, it:

1. Takes your **text description** of the problem
2. Analyzes your **uploaded photo** of internal components using Gemini Vision
3. Searches a **curated knowledge base** of repair manuals and technical documentation
4. Returns a **structured expert diagnosis** with causes, fixes, difficulty ratings, and a service-center verdict

### How it is different from just using ChatGPT or Gemini directly

| Feature | ChatGPT / Gemini | RepairAI |
|---|---|---|
| Knowledge source | General training data | Your repair manuals + curated knowledge base |
| Image analysis | Generic | Focused on internal component damage detection |
| Output format | Varies | Always structured: Causes → Fixes → Verdict |
| Grounding | Can hallucinate | Retrieved from verified documents first |
| Verdict | Never commits | ✅ "User can fix" vs "Go to service center" |
| Knowledge base | Fixed | Expandable — add your own PDFs anytime |

---

## 🏗️ Architecture

```
User Input: Text description + Component Image
                    │
        ┌───────────┴───────────┐
        │                       │
  Gemini Vision            ChromaDB RAG
  (image analysis)    (knowledge retrieval)
        │                       │
        └───────────┬───────────┘
                    │
          Combined Context
                    │
          Gemini 2.5 Flash
          (structured diagnosis)
                    │
     ┌──────────────┼──────────────┐
     │              │              │
  Causes         Fixes         Verdict
```

### Tech Stack

| Component | Technology |
|---|---|
| **UI** | Streamlit |
| **Vision AI** | Google Gemini 2.5 Flash (multimodal) |
| **LLM** | Google Gemini 2.5 Flash |
| **Embeddings** | Google `gemini-embedding-001` |
| **Vector DB** | ChromaDB (local) |
| **RAG Framework** | LangChain |
| **Image Processing** | Pillow |

---

## 📂 Project Structure

```
RAG based Repair Assistant/
│
├── app.py                  # Main Streamlit application
├── build_db.py             # Script to build the ChromaDB vector store
├── run.bat                 # One-click launcher (Windows)
│
├── .env                    # Your API keys (NOT uploaded to GitHub)
├── .env.example            # Template — copy this to .env and fill in keys
├── .gitignore              # Prevents secrets and build files from being committed
├── requirements.txt        # Python dependencies
│
├── data/                   # PDF repair manuals (source documents for RAG)
│   ├── repair.pdf
│   ├── PC Hardware...pdf
│   └── latitude-lm...pdf
│
├── knowledge/              # Custom text knowledge files (also indexed by RAG)
│   ├── laptop_issues.txt
│   ├── desktop_issues.txt
│   ├── mobile_issues.txt
│   └── general_electronics.txt
│
└── chroma_db/              # Vector database (auto-generated, NOT in GitHub)
```

---

## ⚙️ Setup Instructions (For New Developers)

### Prerequisites

- Python 3.10 or higher
- A Google Gemini API key (free tier works, get it at [aistudio.google.com](https://aistudio.google.com))
- A Roboflow API key (for future object detection integration)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/RepairAI.git
cd RepairAI
```

---

### Step 2 — Create a Virtual Environment

It is strongly recommended to use the virtual environment on the D drive (or whichever drive has space):

```bash
# Windows — create venv in project folder
python -m venv .venv

# Activate it
.venv\Scripts\activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up Your API Keys

Copy the example env file and fill in your own keys:

```bash
# Windows
copy .env.example .env
```

Now open `.env` in any text editor and replace the placeholders:

```env
GOOGLE_API_KEY=your_actual_google_api_key_here
ROBOFLOW_API_KEY=your_actual_roboflow_api_key_here
```

> **How to get a Google API Key:**
> 1. Go to [aistudio.google.com](https://aistudio.google.com)
> 2. Click "Get API Key" → Create API key
> 3. Copy and paste it into `.env`

---

### Step 5 — Add Repair Documents to `data/`

Place any PDF repair manuals, device guides, or technical documents into the `data/` folder.  
You can also add `.txt` knowledge files to the `knowledge/` folder.

> The more relevant documents you add, the better the diagnoses will be.

---

### Step 6 — Build the Vector Database

This step indexes all your documents into ChromaDB. **Run it once before launching the app.**

```bash
# Make sure your .venv is active first
python build_db.py
```

> ⚠️ **Important:** This uses the Google Embedding API and has rate limits on the free tier (100 requests/minute).  
> For large document sets it will take 20–40 minutes. The script is **resumable** — if it gets interrupted, just run it again and it will skip already-indexed chunks.

---

### Step 7 — Launch the App

**Option A — Double click `run.bat`** (easiest on Windows)

**Option B — Command line:**
```bash
.venv\Scripts\streamlit.exe run app.py --server.port 8502
```

Then open your browser at: **http://localhost:8502**

---

## 🖥️ How to Use the App

1. **Type your device issue** in the text box  
   *Example: "My laptop fan makes a grinding noise and it randomly shuts down"*

2. **Upload a photo** of the internal components (optional but recommended)  
   *Works with: JPG, PNG, WEBP, BMP*

3. **Click "Run AI Diagnosis"**

4. The app will show:
   - 🔬 **Component Image Analysis** — what the AI sees in your photo
   - ⚠️ **Possible Causes** — ranked by likelihood
   - 🛠️ **Recommended Fixes** — step-by-step with difficulty tags `[EASY]` `[MEDIUM]` `[HARD]`
   - ✅ / 🏥 **Verdict** — User can fix it OR go to service center
   - 💡 **Prevention Tips**

---

## 🔌 Adding New Knowledge (Expanding the Knowledge Base)

### Option 1 — Add PDF files
Drop any PDF (repair manual, service guide, datasheet) into the `data/` folder, then re-run:
```bash
python build_db.py
```

### Option 2 — Add text knowledge files
Create a `.txt` file in the `knowledge/` folder following this format:

```
ISSUE: [describe the problem]
COMPONENT: [which component is involved]
CAUSES:
- Cause 1
- Cause 2
FIX:
1. Step one
2. Step two
DIFFICULTY: Easy / Medium / Hard
SERVICE_CENTER_REQUIRED: Yes / No
```

Then re-run `python build_db.py`.

---

## 🔮 Roboflow Integration (Coming Soon)

A Roboflow object detection model has been trained to detect internal device components from photos. The planned integration will:

1. Auto-detect components visible in the uploaded image (CPU, RAM, battery, charging port, etc.)
2. Pass the detected component names directly into the RAG query
3. Show bounding boxes around detected components in the UI

**To integrate (when ready):**

```python
# In app.py, replace the vision analysis call with:
from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)
result = client.infer(image_path, model_id="your-model-id/version")
detected_components = [pred["class"] for pred in result["predictions"]]
```

---

## 🛠️ Troubleshooting

### "Diagnosis failed: 404 model not found"
The Gemini model name changed. Run this to check available models:
```python
import google.genai as genai, os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
for m in client.models.list():
    print(m.name)
```
Then update the model name in `app.py` (search for `gemini-2.5-flash`).

### "Diagnosis failed: 429 RESOURCE_EXHAUSTED"
You've hit the free-tier rate limit. Options:
- Wait a minute and try again (per-minute limit)
- Wait until next day (daily limit resets at midnight UTC)
- Upgrade to a paid Gemini API plan

### "Could not load knowledge base — run build_db.py first"
The `chroma_db/` folder is missing. Run:
```bash
python build_db.py
```

### build_db.py keeps hitting rate limits
The script is resumable. Just re-run it — it will skip chunks that are already indexed and continue from where it stopped.

---

## 🚀 Future Scope

- [ ] Roboflow object detection integration
- [ ] Chain-of-Thought reasoning for more transparent diagnoses
- [ ] Tree-of-Thought for multi-hypothesis evaluation
- [ ] Multi-device knowledge bases (phones, TVs, appliances)
- [ ] Repair cost estimator
- [ ] Voice input support
- [ ] Local LLM support (Ollama / LLaMA) for offline use
- [ ] AR camera overlay to highlight faulty components in real time
- [ ] Predictive maintenance from component photos
- [ ] Technician marketplace integration

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

Built with:
- [Streamlit](https://streamlit.io) — UI framework
- [LangChain](https://langchain.com) — RAG pipeline
- [ChromaDB](https://trychroma.com) — vector database
- [Google Gemini](https://aistudio.google.com) — LLM + Vision + Embeddings
- [Roboflow](https://roboflow.com) — Object detection (coming soon)
#   R e p a i r - A s s i s t a n t  
 