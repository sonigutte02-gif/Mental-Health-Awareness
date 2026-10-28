@echo off
echo ════════════════════════════════════════════════════
echo   MindBridge AI — Mental Health Awareness Chatbot
echo   Powered by IBM Granite LLM and IBM WatsonX AI
echo ════════════════════════════════════════════════════
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting MindBridge AI on http://localhost:5001
echo Press Ctrl+C to stop the server.
echo.
python app.py
