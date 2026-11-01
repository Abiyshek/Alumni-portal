#!/bin/bash

# Alumni ML Platform - Startup Script for Unix/Linux/Mac
# This script starts both the Flask backend and React frontend

echo ""
echo "==============================================="
echo "  Alumni ML Platform - Starting Services"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found. Please install Node.js 14+"
    exit 1
fi

echo "[1/4] Checking directories..."
if [ ! -d "backend" ]; then
    echo "[ERROR] backend/ directory not found"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "[ERROR] frontend/ directory not found"
    exit 1
fi

echo "        ✓ Directories verified"

echo ""
echo "[2/4] Installing/Checking Python dependencies..."
cd backend
pip install -q Flask Flask-CORS PyJWT python-dotenv 2>/dev/null
cd ..
echo "        ✓ Python dependencies ready"

echo ""
echo "[3/4] Installing/Checking Node.js dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "        Installing npm packages (this may take a minute)..."
    npm install --silent
fi
cd ..
echo "        ✓ Node.js dependencies ready"

echo ""
echo "[4/4] Starting services..."
echo ""

# Start Flask backend in background
echo "Starting Flask Backend on http://localhost:5000"
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Start React frontend in background
echo "Starting React Frontend on http://localhost:3000"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "==============================================="
echo "  Services Started!"
echo "==============================================="
echo ""
echo "Backend (Flask):  http://localhost:5000"
echo "Frontend (React): http://localhost:3000"
echo ""
echo "Test credentials:"
echo "  Email: user@alumni.edu"
echo "  Password: user123"
echo ""
echo "Process IDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "To stop services, run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for user interrupt
wait
