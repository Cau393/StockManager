# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Stock Management Application

This file configures PyInstaller to create a standalone executable.
"""

import sys
from os import path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['sqlalchemy.sql.default_comparator', 'PySide6.QtCharts'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='stock_manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# For macOS, create a .app bundle
app = BUNDLE(
    exe,
    name='StockManager.app',
    icon=None,
    bundle_identifier='com.stockmanager.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
        'CFBundleShortVersionString': '1.0.0',
    },
)