@echo off
echo ===================================================
echo Starting SentinelMind AI (Backend + Frontend)
echo ===================================================
cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "SentinelMind Backend" cmd /k ".\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching SentinelMind Studio Frontend on http://localhost:3000 ...
cd frontend
start "SentinelMind Frontend" cmd /k "npm start"

echo.
echo ===================================================
echo Services initiated!
echo Backend:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo Frontend: http://localhost:3000
echo ===================================================
