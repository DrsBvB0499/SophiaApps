# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for CodeAap
# Build: pyinstaller codeaap.spec   (run from the codeaap/ directory)

import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Bundle the read-only data folder (levels.json) and empty asset dirs.
# The writable progress.json is written next to the .exe at runtime.
added_files = [
    (os.path.join("data", "levels.json"), "data"),
    ("assets",                             "assets"),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        "pygame",
        "pygame.mixer",
        "pygame.font",
        "pygame.draw",
        "pygame.transform",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Only exclude things that are truly never needed.
    # Do NOT exclude stdlib modules (urllib, email, http, etc.) —
    # PyInstaller's own pyi_rth_pkgres runtime hook needs them internally.
    excludes=["tkinter", "numpy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CodeAap",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no black terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # add .ico path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CodeAap",
)
