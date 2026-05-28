@echo off
echo Starting AI Repair Assistant...
call .venv\Scripts\activate
streamlit run frontend\app.py --server.port 8502
pause
