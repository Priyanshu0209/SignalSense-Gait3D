# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/priyanshu/Projects/SignalSense-Gait3D/launcher.py'],
    pathex=['/home/priyanshu/Projects/SignalSense-Gait3D/backend'],
    binaries=[],
    datas=[('/home/priyanshu/Projects/SignalSense-Gait3D/frontend/dist', 'frontend/dist'), ('/home/priyanshu/Projects/SignalSense-Gait3D/frontend/public', 'frontend/public')],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off', 'webview', 'webview.platforms.qt', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebChannel', 'qtpy', 'app.main', 'app.models.domain', 'aiosqlite', 'sqlalchemy.ext.asyncio', 'pydantic', 'pydantic_settings', 'cryptography'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SignalSense',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
