import os
import sys

# Configure environment before importing FastAPI app
os.environ["VITE_API_URL"] = "http://127.0.0.1:8000/api/v1"

# Add backend to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
