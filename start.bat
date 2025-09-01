@echo off
echo 🎙️ AI News Reporter - Quick Start Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Error: Python not found. Please install Python 3.9+ first.
        pause
        exit /b 1
    )
)

echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 📚 Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo 🚀 Starting AI News Reporter...
echo ✅ Backend will start on: http://localhost:1234
echo ✅ Frontend will open on: http://localhost:8080
echo.
echo Press Ctrl+C to stop the servers
echo ========================================
echo.

REM Start backend in background
echo Starting backend server...
start "AI News Backend" cmd /k "call .venv\Scripts\activate.bat && python backend.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
call .venv\Scripts\activate.bat
streamlit run frontend.py --server.port 8080

pause
