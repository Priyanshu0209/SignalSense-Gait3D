import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
DIST_DIR = ROOT_DIR / "backend" / "dist"

def main():
    print("Building SignalSense Backend Engine...")
    
    # Path to the PyInstaller executable within the venv
    if os.name == 'nt':
        pyinstaller_exe = ROOT_DIR / ".venv" / "Scripts" / "pyinstaller.exe"
    else:
        pyinstaller_exe = ROOT_DIR / ".venv" / "bin" / "pyinstaller"

    if not pyinstaller_exe.exists():
        print("Error: PyInstaller not found. Ensure it is installed in .venv")
        sys.exit(1)

    cmd = [
        str(pyinstaller_exe),
        "--name", "signalsense-engine",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--distpath", str(DIST_DIR),
        str(BACKEND_DIR / "app" / "main.py")
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("Backend engine built successfully!")
    else:
        print("Error building backend engine.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
