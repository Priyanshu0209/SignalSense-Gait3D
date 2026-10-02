import os
import sys
import subprocess
import threading
import time
import socket

# Configure environment before importing FastAPI app
os.environ["VITE_API_URL"] = "http://127.0.0.1:8000/api/v1"

# Add backend to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.main import app
import uvicorn

PORT = 8000
URL = f"http://127.0.0.1:{PORT}"

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    try:
        if is_port_in_use(PORT):
            print(f"Port {PORT} already in use.")
            return
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    except Exception as e:
        print(f"Server error: {e}")

def wait_for_server(timeout=20):
    """Poll until backend responds on /health"""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{URL}/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.3)
    return False

def open_browser():
    """Open Chrome in app mode (no browser chrome/toolbar = feels native)"""
    # Try Chrome app mode first — looks like a proper app, not a browser tab
    browsers = [
        ["google-chrome", f"--app={URL}", "--window-size=1400,900",
         "--no-first-run", "--no-default-browser-check"],
        ["chromium-browser", f"--app={URL}", "--window-size=1400,900"],
        ["chromium", f"--app={URL}", "--window-size=1400,900"],
        ["firefox", "--new-window", URL],
        ["xdg-open", URL],
    ]
    for cmd in browsers:
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Opened with: {cmd[0]}")
            return
        except FileNotFoundError:
            continue
    print(f"Could not open browser. Please open manually: {URL}")

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║   SignalSense — Enterprise Wi-Fi Analytics   ║")
    print("╚══════════════════════════════════════════════╝")

    # Start backend in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("⏳ Starting backend...")
    if not wait_for_server(timeout=25):
        print("❌ Backend failed to start.")
        sys.exit(1)

    print(f"✅ Ready — opening at {URL}")
    open_browser()

    # Keep main thread alive (backend thread is daemon, will stop with this)
    print("   Press Ctrl+C to quit.\n")
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down SignalSense.")
        sys.exit(0)
