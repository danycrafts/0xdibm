# -*- mode: python ; coding: utf-8 -*-

import sys
block_cipher = None

# Collect all necessary data files
added_files = [
    ('resources/assets', 'resources/assets'),  # Include the assets folder and all its contents
]

a = Analysis(
    ['app.py'],  # Replace with your actual entry point file
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['tkinter', 'ttkbootstrap', 'pandas', 'psutil', 'aiohttp', 'openai', 'python-pptx', 'pdfplumber'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

# Windows specific configuration
if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,  # Changed this to True
        name='app',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='resources\\assets\\favicon.ico',  # Assuming you have an icon in the assets folder
    )
    
    collect = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='app',
    )
    
# Linux specific configuration
elif sys.platform.startswith('linux'):
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,  # Changed this to True
        name='app',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
    )

    collect = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='app',
    )