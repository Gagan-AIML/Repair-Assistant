# app.py
# RepairAI — Smart Multimodal Device Diagnosis & Repair Workflow Assistant
# Entrypoint and Streamlit UI Orchestrator

import io
import os
import time
import streamlit as st
from PIL import Image

import sys

# Add root directory to python path so we can import from backend and frontend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Modular Pipeline Engines
from frontend.styles import STYLE_CSS
from backend.engines.yolo_detector import detect_components_with_yolo
from backend.engines.ocr_extractor import extract_ocr_context_with_gemini
from backend.engines.rag_engine import load_vectorstore, run_rag_diagnosis
from frontend.formatters import format_causes_html, format_fixes_html, format_tips_html, format_verdict_html, format_vision_analysis_html

# ─────────────────────────────────────────────
#  PAGE CONFIG & STYLING
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RepairAI — Smart Device Diagnosis",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(STYLE_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <p class="hero-title">🔧 RepairAI</p>
  <p class="hero-subtitle">
    AI-Powered Multimodal Device Diagnosis & Repair Workflow Engine
  </p>
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <div class="pipeline-icon">📸</div>
      <div class="pipeline-label">Image Upload</div>
    </div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step">
      <div class="pipeline-icon">🔍</div>
      <div class="pipeline-label">YOLO Detection</div>
    </div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step">
      <div class="pipeline-icon">📝</div>
      <div class="pipeline-label">OCR Extraction</div>
    </div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step">
      <div class="pipeline-icon">🧠</div>
      <div class="pipeline-label">RAG Retrieval</div>
    </div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step">
      <div class="pipeline-icon">🛠️</div>
      <div class="pipeline-label">Repair Workflow</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "diagnosis_results" not in st.session_state:
    st.session_state["diagnosis_results"] = None

# ─────────────────────────────────────────────
#  INPUT SECTION — Two columns
# ─────────────────────────────────────────────
input_col1, input_col2 = st.columns([1, 1], gap="large")

with input_col1:
    st.markdown("""
    <div class="input-card">
      <div class="card-label">📝 Describe the Issue</div>
    </div>
    """, unsafe_allow_html=True)
    user_issue = st.text_area(
        label="issue_input",
        label_visibility="collapsed",
        placeholder="e.g., My laptop suddenly stopped turning on. The charging LED was blinking but now it's completely dead...",
        height=180,
        key="issue_text"
    )

with input_col2:
    st.markdown("""
    <div class="input-card">
      <div class="card-label">📸 Component Image Input</div>
    </div>
    """, unsafe_allow_html=True)
    
    input_method = st.radio(
        "Choose input method:",
        ["📂 Upload Image File", "📷 Capture Live Photo"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    image_bytes = None
    
    if input_method == "📂 Upload Image File":
        uploaded_file = st.file_uploader(
            label="component_image",
            label_visibility="collapsed",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            help="Upload a photo of the internal components (motherboard, PCB, battery area, etc.)"
        )
        if uploaded_file:
            uploaded_file.seek(0)
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption="📷 Uploaded Image Preview", use_container_width=True)
    else:
        captured_file = st.camera_input(
            label="Capture Motherboard Photo",
            label_visibility="collapsed"
        )
        if captured_file:
            captured_file.seek(0)
            image_bytes = captured_file.read()

# CTA Button — full width
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    diagnose_btn = st.button("🔍  RUN AI DIAGNOSIS", key="diagnose_btn")

# ─────────────────────────────────────────────
#  RUN PIPELINE
# ─────────────────────────────────────────────
if diagnose_btn:
    if not user_issue.strip():
        st.error("⚠️ Please describe your device issue before running diagnosis.")
        st.stop()

    with st.spinner("Loading knowledge base..."):
        try:
            vectorstore = load_vectorstore()
        except Exception as e:
            st.error(f"❌ Could not load knowledge base. Run `build_db.py` first.\n\nError: {e}")
            st.stop()

    progress_bar = st.progress(0, text="🔄 Initializing AI Pipeline...")
    status_placeholder = st.empty()

    annotated_img = None
    detected_components = []
    ocr_context = ""
    vision_analysis = ""

    if image_bytes:

        # Parallel Execution of Steps 1, 2, and 3
        progress_bar.progress(25, text="🔬 Running Parallel AI Vision Pipelines...")
        status_placeholder.markdown('<div class="status-badge status-active">⚡ Running YOLO Detection, OCR, and AI Damage Analysis concurrently...</div>', unsafe_allow_html=True)
        
        import concurrent.futures
        
        def run_vision_analysis():
            import google.genai as genai
            from google.genai import types as genai_types
            from dotenv import load_dotenv
            import os
            
            load_dotenv(override=True)
            fresh_key = os.getenv("GOOGLE_API_KEY")
            client = genai.Client(api_key=fresh_key)
            
            vision_prompt = f"""
            You are an expert electronics repair technician.
            The user reported: "{user_issue}"
            Analyze this image and identify visual defects: burns, swollen caps, cracks, corrosion, dust blockages, or loose connectors.
            Be specific about component locations and severity.
            """
            image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[vision_prompt, image_part]
            )
            return response.text

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_yolo = executor.submit(detect_components_with_yolo, image_bytes, user_issue)
            future_ocr = executor.submit(extract_ocr_context_with_gemini, image_bytes)
            future_vision = executor.submit(run_vision_analysis)

            # Wait for all futures to complete (with safety timeout)
            try:
                annotated_img, detected_components = future_yolo.result(timeout=15)
            except Exception as e:
                st.warning(f"⚠️ YOLO detection failed: {e}")
                annotated_img, detected_components = None, []

            try:
                ocr_context = future_ocr.result(timeout=15)
            except Exception:
                ocr_context = "OCR Extraction unavailable: API offline or rate-limited."

            try:
                vision_analysis = future_vision.result(timeout=15)
            except Exception:
                vision_analysis = "Vision damage analysis unavailable: API offline or rate-limited."
    else:
        vision_analysis = "No image provided. Diagnosis based on text description only."
        ocr_context = "No image provided."
        detected_components = []

    # Step 4 & 5: RAG + LLM Generation
    progress_bar.progress(70, text="🧠 Step 4/5 — RAG Knowledge Retrieval...")
    status_placeholder.markdown('<div class="status-badge status-active">🧠 Querying repair knowledge base with multimodal context...</div>', unsafe_allow_html=True)
    try:
        sections = run_rag_diagnosis(user_issue, vision_analysis, detected_components, ocr_context, vectorstore)
    except Exception as e:
        st.error(f"❌ Diagnosis generation failed: {e}")
        st.stop()

    progress_bar.progress(95, text="🛠️ Step 5/5 — Generating Repair Workflow...")
    time.sleep(0.3)

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

    st.session_state["diagnosis_results"] = {
        "annotated_image": annotated_img,
        "detected_components": detected_components,
        "ocr_context": ocr_context,
        "vision_analysis": vision_analysis,
        "sections": sections,
        "is_user_fix": is_user_fix,
        "device_type": device_type
    }

    progress_bar.progress(100, text="✅ Diagnosis Complete!")
    status_placeholder.markdown('<div class="status-badge status-done">✅ Full 5-step pipeline completed successfully!</div>', unsafe_allow_html=True)
    time.sleep(0.5)
    progress_bar.empty()
    status_placeholder.empty()

# ══════════════════════════════════════════
#  DISPLAY RESULTS — Full Width Below Input
# ══════════════════════════════════════════
results = st.session_state["diagnosis_results"]
if results:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="results-title-bar">
      <h2>🧠 AI Diagnosis Report</h2>
      <div class="title-line"></div>
    </div>
    """, unsafe_allow_html=True)

    sections = results["sections"]
    is_user_fix = results["is_user_fix"]
    device_type = results["device_type"]

    # Pipeline Summary Bar
    comp_count = len(results["detected_components"])
    has_ocr = bool(results["ocr_context"] and "No image" not in results["ocr_context"])
    has_vision = bool(results["vision_analysis"] and "No image" not in results["vision_analysis"])

    st.markdown(f"""
    <div class="pipeline-summary">
      <div class="summary-chip"><span class="chip-dot chip-green"></span> YOLO: {comp_count} components</div>
      <div class="summary-chip"><span class="chip-dot {'chip-green' if has_ocr else 'chip-red'}"></span> OCR: {'Active' if has_ocr else 'N/A'}</div>
      <div class="summary-chip"><span class="chip-dot {'chip-green' if has_vision else 'chip-red'}"></span> Vision: {'Active' if has_vision else 'N/A'}</div>
      <div class="summary-chip"><span class="chip-dot chip-green"></span> RAG: Retrieved</div>
      <div class="summary-chip"><span class="chip-dot chip-green"></span> LLM: Generated</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column results layout ──
    res_left, res_right = st.columns([1, 1], gap="large")

    with res_left:
        # 1. YOLO Detection
        if results["annotated_image"] or results["detected_components"]:
            st.markdown('<div class="result-section result-vision">', unsafe_allow_html=True)
            st.markdown('<div class="result-header">🔍 YOLO Component Detection</div>', unsafe_allow_html=True)
            if results["annotated_image"]:
                st.image(results["annotated_image"], caption="📷 YOLO Bounding Box Detections", use_column_width=True)
            if results["detected_components"]:
                chips_html = "".join([f'<span class="component-chip">🧩 {c}</span>' for c in results["detected_components"]])
                st.markdown(f'<div class="chip-container">{chips_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#64748b; font-size:0.9rem;">No components detected visually.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 2. OCR
        if has_ocr:
            ocr_lines = results["ocr_context"].split('\n')
            formatted_ocr = "".join([
                f'<div class="ocr-line"><span class="ocr-prompt">❯</span> {l.strip()}</div>'
                for l in ocr_lines if l.strip()
            ])
            st.markdown(f"""
            <div class="result-section result-ocr">
              <div class="result-header" style="color:#22d3ee;">📝 OCR Context Extraction</div>
              <div class="ocr-terminal">
                <div class="terminal-header">
                  <span class="terminal-dot" style="background:#ef4444;"></span>
                  <span class="terminal-dot" style="background:#eab308;"></span>
                  <span class="terminal-dot" style="background:#22c55e;"></span>
                  <span class="terminal-title">ocr_output.log</span>
                </div>
                <div class="terminal-body">{formatted_ocr}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. Vision Damage Analysis
        if has_vision:
            st.markdown(f"""
            <div class="result-section result-vision-damage">
              <div class="result-header" style="color:#93c5fd;">🔬 Component State Analysis</div>
              {format_vision_analysis_html(results["vision_analysis"])}
            </div>
            """, unsafe_allow_html=True)

    with res_right:
        # 4. Possible Causes
        if sections["causes"]:
            st.markdown(f"""
            <div class="result-section result-causes">
              <div class="result-header">⚠️ Possible Causes</div>
              {format_causes_html(sections['causes'])}
            </div>
            """, unsafe_allow_html=True)

        # 5. Recommended Fixes
        if sections["fixes"]:
            st.markdown(f"""
            <div class="result-section result-fixes">
              <div class="result-header">🛠️ Recommended Fixes</div>
              {format_fixes_html(sections['fixes'], is_user_fix=is_user_fix, device_type=device_type)}
            </div>
            """, unsafe_allow_html=True)

    # ── Full-width sections ──
    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    verdict_col, tips_col = st.columns([1, 1], gap="large")

    with verdict_col:
        # 6. Verdict
        if sections["verdict"]:
            verdict_text = sections["verdict"]
            badge_class = "badge-user" if is_user_fix else "badge-service"
            badge_text = "✅ User Can Fix This" if is_user_fix else "🏥 Go To Service Center"

            st.markdown(f"""
            <div class="result-section result-verdict">
              <div class="result-header">📋 Verdict</div>
              <div style="margin-bottom:1rem;">
                <span class="{badge_class}">{badge_text}</span>
              </div>
              {format_verdict_html(verdict_text)}
            </div>
            """, unsafe_allow_html=True)



    with tips_col:
        # 7. Prevention Tips
        if sections["tips"]:
            st.markdown(f"""
            <div class="result-section" style="border-left:4px solid #8b5cf6;">
              <div class="result-header" style="color:#c4b5fd;">💡 Prevention Tips</div>
              {format_tips_html(sections['tips'])}
            </div>
            """, unsafe_allow_html=True)

    # Fallback
    if not any([sections["causes"], sections["fixes"], sections["verdict"]]):
        st.markdown(f"""
        <div class="result-section result-fixes">
          <div class="result-header">🧠 AI Diagnosis</div>
          <div class="result-body">{sections['raw'].replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # ── EMPTY STATE ──
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon-ring">
        <div class="empty-icon">🔧</div>
      </div>
      <h3 class="empty-title">Ready to Diagnose</h3>
      <p class="empty-desc">
        Describe your device issue and optionally upload an internal component photo<br>
        to receive expert AI-powered repair guidance.
      </p>
      <div class="empty-steps">
        <div class="empty-step">
          <div class="empty-step-num">1</div>
          <div class="empty-step-text">Enter a detailed issue description</div>
        </div>
        <div class="empty-step">
          <div class="empty-step-num">2</div>
          <div class="empty-step-text">Upload a component photo (optional)</div>
        </div>
        <div class="empty-step">
          <div class="empty-step-num">3</div>
          <div class="empty-step-text">Click "Run AI Diagnosis" to begin</div>
        </div>
      </div>
      <div class="empty-features">
        <div class="feature-chip">🔍 YOLO Detection</div>
        <div class="feature-chip">📝 OCR Extraction</div>
        <div class="feature-chip">🧠 RAG Retrieval</div>
        <div class="feature-chip">🔬 Vision Analysis</div>
        <div class="feature-chip">🛠️ Repair Workflow</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
  <div class="footer-line"></div>
  <div class="footer-content">
    <span class="footer-brand">RepairAI</span>
    <span class="footer-sep">·</span>
    <span>Powered by Gemini 2.5 Flash + RAG + YOLO</span>
    <span class="footer-sep">·</span>
    <span>🧠 AI-Powered Device Diagnosis</span>
  </div>
</div>
""", unsafe_allow_html=True)