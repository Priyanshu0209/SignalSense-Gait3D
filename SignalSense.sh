#!/bin/bash
# ============================================================
#  SignalSense - One-Click Desktop Launcher
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT=8000
URL="http://127.0.0.1:$PORT"
PYTHON="$SCRIPT_DIR/.venv/bin/python"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   SignalSense — Enterprise Wi-Fi Analytics   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check setup was done
if [ ! -f "$PYTHON" ]; then
    echo "❌ Virtual environment not found."
    echo "   Please run:  bash setup.sh"
    exit 1
fi

# Kill ALL old instances completely
echo "⏹  Stopping any previous SignalSense instances..."
pkill -f launcher_headless 2>/dev/null
pkill -f launcher.py 2>/dev/null
pkill -f uvicorn 2>/dev/null
sleep 1

# Force-free port 8000 if still in use
if lsof -ti:$PORT &>/dev/null; then
    echo "⚠  Port $PORT still occupied — force killing..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 2
fi

# Start backend server
echo "▶ Starting backend server..."
VITE_API_URL="http://127.0.0.1:$PORT/api/v1" "$PYTHON" "$SCRIPT_DIR/launcher_headless.py" &
SERVER_PID=$!

# Wait for server to be ready (max 25s)
echo "⏳ Waiting for server to be ready..."
READY=0
for i in $(seq 1 50); do
    if curl -s --max-time 1 "$URL/health" > /dev/null 2>&1; then
        READY=1
        break
    fi
    # Also check if the React frontend is up (it serves index.html on /)
    if curl -s --max-time 1 "$URL/" | grep -q "<!doctype html" 2>/dev/null; then
        READY=1
        break
    fi
    sleep 0.5
done

if [ "$READY" -eq 0 ]; then
    echo "❌ Server failed to start."
    echo "   Try running manually: .venv/bin/python launcher_headless.py"
    exit 1
fi

echo "✅ Server ready!"
echo ""
echo "🌐 Opening SignalSense at: $URL"
echo "   Press Ctrl+C in this terminal to stop."
echo ""

# Open Chrome in app mode (no address bar — looks like a native app)
google-chrome \
    --app="$URL" \
    --window-size=1440,900 \
    --no-first-run \
    --no-default-browser-check \
    --disable-extensions \
    --start-maximized \
    2>/dev/null &

# Keep alive
wait $SERVER_PID
