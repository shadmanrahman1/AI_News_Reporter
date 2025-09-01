#!/bin/bash

echo "🎙️ AI News Reporter - Quick Start Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Python3 not found. Please install Python 3.9+ first."
        exit 1
    fi
fi

echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "🚀 Starting AI News Reporter..."
echo "✅ Backend will start on: http://localhost:1234"
echo "✅ Frontend will open on: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the servers"
echo "========================================"
echo ""

# Start backend in background
echo "Starting backend server..."
python backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
streamlit run frontend.py --server.port 8080

# Cleanup: Kill backend when frontend stops
kill $BACKEND_PID 2>/dev/null
