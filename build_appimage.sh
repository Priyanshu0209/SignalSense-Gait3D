#!/bin/bash
set -e

echo "Building PyInstaller Executable..."
source .venv/bin/activate
python build_app.py

echo "Preparing AppDir..."
mkdir -p AppDir/usr/bin
cp dist/SignalSense AppDir/usr/bin/

echo "Creating .desktop file..."
cat > AppDir/signalsense.desktop <<EOF
[Desktop Entry]
Name=SignalSense
Comment=Enterprise Wi-Fi Analytics
Exec=SignalSense
Icon=signalsense
Terminal=false
Type=Application
Categories=Utility;
EOF

echo "Creating Icon..."
cp frontend/public/vite.svg AppDir/signalsense.svg

echo "Creating AppRun..."
cat > AppDir/AppRun <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec SignalSense "$@"
EOF
chmod +x AppDir/AppRun

echo "Downloading appimagetool..."
wget -q -nc https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

echo "Generating AppImage..."
./appimagetool-x86_64.AppImage AppDir SignalSense-x86_64.AppImage

echo "AppImage created successfully at SignalSense-x86_64.AppImage"
