#!/bin/bash
# ============================================================
#  SignalSense - First-Time Setup Script
#  Run this ONCE before launching the app
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   SignalSense — First-Time Setup             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check Python3
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 not found. Install it with: sudo apt install python3 python3-venv python3-full"
    exit 1
fi

# Check Node/npm for frontend build
if ! command -v npm &>/dev/null; then
    echo "⚠  npm not found. Install with: sudo apt install nodejs npm"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "▶ Creating Python virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment already exists."
fi

# Install Python dependencies into venv
echo ""
echo "▶ Installing Python dependencies (this may take a minute)..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt --quiet
echo "✅ Python dependencies installed."

# Build frontend if dist doesn't exist
if [ ! -d "frontend/dist" ]; then
    echo ""
    echo "▶ Building frontend..."
    cd frontend && npm install --silent && npm run build --silent && cd ..
    echo "✅ Frontend built."
else
    echo "✅ Frontend already built."
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅ Setup complete!                          ║"
echo "║                                              ║"
echo "║  To run: ./SignalSense.sh                    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
