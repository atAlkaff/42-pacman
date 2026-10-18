# -*- mode: python ; coding: utf-8 -*-
# PyInstaller packaging script for Steam/Itch.io deployment

block_cipher = None

a = Analysis(
    ['pac-man.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('README.md', '.')
    ],
    hiddenimports=[
        'pydantic',
        'pygame',
        'a_maze_ing' # Ensure the external package is bundled
    ],
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
    name='PacMan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Set to False for a completely windowed app without a terminal
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
