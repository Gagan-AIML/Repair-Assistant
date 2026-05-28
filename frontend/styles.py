# styles.py
# Professional Industry-Grade UI for RepairAI

STYLE_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

  /* ══════════════════════════════════════════════════
     CORE FOUNDATION
  ══════════════════════════════════════════════════ */
  html, body, [data-testid="stAppViewContainer"] {
    background: #0a0e1a !important;
    color: #e2e8f0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }
  [data-testid="stHeader"] {
    background: rgba(10,14,26,0.85) !important;
    backdrop-filter: blur(24px) !important;
    border-bottom: 1px solid rgba(99,102,241,0.08);
  }
  [data-testid="stSidebar"] { display: none !important; }
  
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 10px; }

  /* ══════════════════════════════════════════════════
     HERO HEADER
  ══════════════════════════════════════════════════ */
  .hero-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 50%, rgba(6,182,212,0.05) 100%);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
  }
  .hero-banner::after {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.06), transparent);
    animation: shimmer 6s infinite;
  }
  @keyframes shimmer { 0%{left:-100%} 100%{left:200%} }

  .hero-title {
    font-family: 'Inter', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    background: linear-gradient(135deg, #c7d2fe 0%, #818cf8 40%, #a78bfa 70%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
    margin-top: 0.6rem;
    letter-spacing: 0.01em;
  }

  /* Pipeline Flow */
  .pipeline-flow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    margin-top: 1.8rem;
    flex-wrap: wrap;
  }
  .pipeline-step {
    display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
    padding: 0.5rem 1rem;
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 10px;
    transition: all 0.3s ease;
  }
  .pipeline-step:hover { background: rgba(99,102,241,0.1); transform: translateY(-2px); }
  .pipeline-icon { font-size: 1.3rem; }
  .pipeline-label {
    font-size: 0.65rem; font-weight: 700; color: #94a3b8;
    letter-spacing: 0.08em; text-transform: uppercase;
  }
  .pipeline-arrow { color: rgba(99,102,241,0.35); font-size: 1.1rem; }

  /* ══════════════════════════════════════════════════
     INPUT SECTION
  ══════════════════════════════════════════════════ */
  .input-card {
    margin-bottom: 0.3rem;
  }
  .card-label {
    font-size: 0.8rem; font-weight: 700; color: #818cf8;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin-bottom: 0.6rem;
    display: flex; align-items: center; gap: 0.5rem;
  }
  .card-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(99,102,241,0.25), transparent);
  }

  textarea {
    background: rgba(15,20,35,0.8) !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    font-size: 1rem !important;
    line-height: 1.7 !important;
    padding: 1.2rem !important;
  }
  textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
  }
  textarea::placeholder { color: #475569 !important; }

  [data-testid="stFileUploader"] {
    background: rgba(15,20,35,0.6) !important;
    border: 2px dashed rgba(99,102,241,0.2) !important;
    border-radius: 14px !important;
    padding: 1.2rem !important;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: #6366f1 !important;
    background: rgba(15,20,35,0.8) !important;
  }

  /* CTA Button */
  div.stButton > button {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(135deg, #6366f1, #4f46e5, #7c3aed) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.85rem 2rem !important;
    border-radius: 14px !important;
    border: none !important;
    width: 100% !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
    transition: all 0.3s ease !important;
  }
  div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.5) !important;
  }

  /* ══════════════════════════════════════════════════
     SECTION DIVIDER
  ══════════════════════════════════════════════════ */
  .section-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(99,102,241,0.2), transparent);
    margin: 2.5rem 0;
  }
  .styled-divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(99,102,241,0.2), transparent);
    margin: 2rem 0;
  }

  /* ══════════════════════════════════════════════════
     PIPELINE SUMMARY BAR
  ══════════════════════════════════════════════════ */
  .pipeline-summary {
    display: flex; flex-wrap: wrap; gap: 0.6rem;
    padding: 1rem 1.2rem;
    background: rgba(15,20,35,0.6);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 14px;
    margin-bottom: 2rem;
  }
  .summary-chip {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.8rem; font-weight: 600; color: #94a3b8;
    padding: 0.35rem 0.9rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
  }
  .chip-dot { width: 8px; height: 8px; border-radius: 50%; }
  .chip-green { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); }
  .chip-red { background: #64748b; }

  /* ══════════════════════════════════════════════════
     RESULT CARDS — The main visual upgrade
  ══════════════════════════════════════════════════ */
  .result-section {
    background: rgba(15,20,35,0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.8rem;
    transition: border-color 0.3s ease;
  }
  .result-section:hover {
    border-color: rgba(255,255,255,0.1);
  }
  .result-header {
    font-family: 'Inter', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    letter-spacing: -0.02em;
    display: flex; align-items: center; gap: 0.5rem;
  }
  .result-body {
    color: #cbd5e1;
    font-size: 1.02rem;
    line-height: 1.85;
  }

  /* Accent borders */
  .result-vision       { border-left: 4px solid #6366f1; }
  .result-causes       { border-left: 4px solid #f59e0b; }
  .result-fixes        { border-left: 4px solid #10b981; }
  .result-verdict      { border-left: 4px solid #8b5cf6; }
  .result-ocr          { border-left: 4px solid #06b6d4; }
  .result-vision-damage{ border-left: 4px solid #3b82f6; }

  .result-vision .result-header       { color: #a5b4fc; }
  .result-causes .result-header       { color: #fbbf24; }
  .result-fixes .result-header        { color: #34d399; }
  .result-verdict .result-header      { color: #c4b5fd; }
  .result-vision-damage .result-header{ color: #93c5fd; }

  /* ══════════════════════════════════════════════════
     CAUSE CARDS
  ══════════════════════════════════════════════════ */
  .cause-card {
    background: rgba(245,158,11,0.04);
    border: 1px solid rgba(245,158,11,0.12);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.8rem;
    display: flex; gap: 1.1rem; align-items: flex-start;
    transition: all 0.25s ease;
  }
  .cause-card:hover {
    background: rgba(245,158,11,0.07);
    border-color: rgba(245,158,11,0.25);
    transform: translateX(3px);
  }
  .cause-num {
    background: linear-gradient(135deg, #d97706, #f59e0b);
    color: #0a0e1a; font-weight: 800; font-size: 0.8rem;
    min-width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 1px;
    box-shadow: 0 2px 8px rgba(245,158,11,0.3);
  }
  .cause-title {
    color: #fbbf24; font-weight: 700; font-size: 1.05rem;
    margin-bottom: 0.35rem; letter-spacing: -0.01em;
  }
  .cause-desc {
    color: #94a3b8; font-size: 0.95rem; line-height: 1.7;
  }

  /* ══════════════════════════════════════════════════
     FIX GROUPS & STEPS
  ══════════════════════════════════════════════════ */
  .fix-group {
    background: rgba(16,185,129,0.04);
    border: 1px solid rgba(16,185,129,0.12);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
  }
  .fix-group-title {
    color: #34d399; font-weight: 700; font-size: 1.1rem;
    margin-bottom: 1.2rem; padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(16,185,129,0.1);
    display: flex; justify-content: space-between; align-items: center;
  }
  .fix-step {
    display: flex; gap: 1rem; align-items: flex-start;
    padding: 0.7rem 0;
  }
  .fix-step-container + .fix-step-container {
    border-top: 1px solid rgba(16,185,129,0.06);
  }
  .step-num {
    background: linear-gradient(135deg, #059669, #10b981);
    color: #0a0e1a; font-weight: 800; font-size: 0.75rem;
    min-width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
    box-shadow: 0 2px 6px rgba(16,185,129,0.25);
  }
  .step-text {
    color: #cbd5e1; font-size: 0.98rem; line-height: 1.75;
  }

  /* Difficulty Badges */
  .diff-badge {
    font-size: 0.7rem; font-weight: 800; padding: 0.2rem 0.75rem;
    border-radius: 20px; letter-spacing: 0.06em; text-transform: uppercase;
  }
  .diff-easy   { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
  .diff-medium { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
  .diff-hard   { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }

  /* ══════════════════════════════════════════════════
     VERDICT
  ══════════════════════════════════════════════════ */
  .badge-user {
    background: rgba(16,185,129,0.1); color: #34d399;
    border: 1px solid rgba(16,185,129,0.25);
    font-size: 0.95rem; font-weight: 700;
    padding: 0.5rem 1.2rem; border-radius: 10px;
    display: inline-block;
    box-shadow: 0 2px 10px rgba(16,185,129,0.1);
  }
  .badge-service {
    background: rgba(239,68,68,0.1); color: #f87171;
    border: 1px solid rgba(239,68,68,0.25);
    font-size: 0.95rem; font-weight: 700;
    padding: 0.5rem 1.2rem; border-radius: 10px;
    display: inline-block;
    box-shadow: 0 2px 10px rgba(239,68,68,0.1);
  }
  .verdict-detail {
    background: rgba(139,92,246,0.04);
    border: 1px solid rgba(139,92,246,0.1);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-top: 1rem;
    color: #cbd5e1;
    font-size: 1rem;
    line-height: 1.8;
  }

  /* ══════════════════════════════════════════════════
     TIPS
  ══════════════════════════════════════════════════ */
  .tip-item {
    display: flex; gap: 1rem; align-items: flex-start;
    padding: 0.8rem 0;
  }
  .tip-item + .tip-item { border-top: 1px solid rgba(139,92,246,0.08); }
  .tip-icon {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    color: #fff; font-size: 0.75rem;
    min-width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
    box-shadow: 0 2px 6px rgba(139,92,246,0.3);
  }
  .tip-text { color: #cbd5e1; font-size: 0.98rem; line-height: 1.75; }

  /* ══════════════════════════════════════════════════
     OCR TERMINAL
  ══════════════════════════════════════════════════ */
  .ocr-terminal {
    border-radius: 12px; overflow: hidden;
    border: 1px solid rgba(6,182,212,0.15);
  }
  .terminal-header {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.6rem 1rem;
    background: rgba(0,0,0,0.5);
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
  .terminal-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; color: #64748b; margin-left: 0.4rem;
  }
  .terminal-body {
    padding: 1rem 1.2rem;
    background: rgba(5,7,12,0.8);
    max-height: 240px; overflow-y: auto;
  }
  .ocr-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem; color: #67e8f9;
    padding: 0.25rem 0; line-height: 1.6;
  }
  .ocr-prompt { color: #22d3ee; margin-right: 0.5rem; font-weight: 700; }

  /* ══════════════════════════════════════════════════
     COMPONENT CHIPS
  ══════════════════════════════════════════════════ */
  .chip-container { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
  .component-chip {
    font-size: 0.82rem; font-weight: 600;
    padding: 0.35rem 1rem; border-radius: 20px;
    background: rgba(99,102,241,0.1); color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.2);
  }

  /* ══════════════════════════════════════════════════
     STATUS BADGES (Pipeline Progress)
  ══════════════════════════════════════════════════ */
  .status-badge {
    font-size: 0.9rem; font-weight: 600;
    padding: 0.7rem 1.2rem; border-radius: 12px;
    margin-bottom: 0.8rem;
  }
  .status-active {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    color: #a5b4fc;
  }
  .status-done {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.18);
    color: #34d399;
  }

  /* ══════════════════════════════════════════════════
     EMPTY STATE
  ══════════════════════════════════════════════════ */
  .empty-state {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 4rem 2rem; text-align: center;
    min-height: 450px;
  }
  .empty-icon-ring {
    width: 110px; height: 110px; border-radius: 50%;
    border: 2px solid rgba(99,102,241,0.2);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1.5rem;
    animation: pulse-ring 3s ease-in-out infinite;
    background: rgba(99,102,241,0.03);
  }
  @keyframes pulse-ring {
    0%,100% { border-color: rgba(99,102,241,0.15); box-shadow: 0 0 0 0 rgba(99,102,241,0); }
    50% { border-color: rgba(99,102,241,0.35); box-shadow: 0 0 25px 5px rgba(99,102,241,0.06); }
  }
  .empty-icon { font-size: 3rem; }
  .empty-title {
    font-size: 1.6rem; font-weight: 700; color: #e2e8f0;
    margin: 0 0 0.5rem;
  }
  .empty-desc {
    color: #64748b; font-size: 1rem;
    line-height: 1.7; max-width: 380px;
  }
  .empty-steps {
    display: flex; flex-direction: column; gap: 0.6rem;
    margin-top: 2rem; width: 100%; max-width: 320px;
  }
  .empty-step {
    display: flex; align-items: center; gap: 0.8rem;
    padding: 0.75rem 1rem;
    background: rgba(99,102,241,0.04);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 12px; transition: all 0.3s ease;
  }
  .empty-step:hover { background: rgba(99,102,241,0.08); }
  .empty-step-num {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: #fff; font-weight: 700; font-size: 0.75rem;
    min-width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .empty-step-text { color: #94a3b8; font-size: 0.9rem; text-align: left; }
  .empty-features {
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 0.5rem; margin-top: 1.8rem;
  }
  .feature-chip {
    font-size: 0.72rem; font-weight: 700;
    padding: 0.3rem 0.8rem; border-radius: 20px;
    background: rgba(139,92,246,0.07); color: #a78bfa;
    border: 1px solid rgba(139,92,246,0.15);
    letter-spacing: 0.04em;
  }

  /* ══════════════════════════════════════════════════
     BRAND LINKS & MAPS
  ══════════════════════════════════════════════════ */
  .brand-link {
    display: block; text-align: center; text-decoration: none !important;
    padding: 0.75rem 0.5rem; border-radius: 12px;
    font-weight: 700; font-size: 0.9rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    color: #cbd5e1 !important; transition: all 0.3s ease;
    margin-bottom: 0.5rem;
  }
  .brand-link:hover {
    transform: translateY(-2px); border-color: rgba(99,102,241,0.3);
    background: rgba(99,102,241,0.06); color: #a5b4fc !important;
  }
  .maps-btn {
    display: block; text-align: center; text-decoration: none !important;
    padding: 0.75rem 1.5rem; border-radius: 12px;
    font-weight: 700; font-size: 0.95rem;
    background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.18);
    color: #f87171 !important; margin-top: 0.8rem; transition: all 0.3s ease;
  }
  .maps-btn:hover { background: rgba(239,68,68,0.12); transform: translateY(-1px); }

  /* City selector */
  .stSelectbox div[data-baseweb="select"] {
    background: rgba(15,20,35,0.8) !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 12px !important;
  }

  /* ══════════════════════════════════════════════════
     FOOTER
  ══════════════════════════════════════════════════ */
  .app-footer { text-align: center; padding: 2rem 0 1rem; margin-top: 1rem; }
  .footer-line {
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(99,102,241,0.15), transparent);
    margin-bottom: 1.2rem;
  }
  .footer-content {
    font-size: 0.82rem; color: #475569;
    display: flex; align-items: center; justify-content: center;
    gap: 0.5rem; flex-wrap: wrap;
  }
  .footer-brand { font-weight: 800; color: #6366f1; }
  .footer-sep { color: #334155; }

  /* ══════════════════════════════════════════════════
     RESULTS HEADER WITH DIVIDER
  ══════════════════════════════════════════════════ */
  .results-title-bar {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 2rem; margin-top: 0.5rem;
  }
  .results-title-bar h2 {
    font-size: 1.5rem; font-weight: 800; color: #e2e8f0;
    margin: 0; white-space: nowrap; letter-spacing: -0.02em;
  }
  .results-title-bar .title-line {
    flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(99,102,241,0.3), transparent);
  }
</style>
"""
