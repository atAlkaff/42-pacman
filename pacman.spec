# -*- mode: python ; coding: utf-8 -*-
# PyInstaller packaging script for the itch.io build.
#
# Build with `make package` (or `uv run pyinstaller --noconfirm pacman.spec`).
# The result is a single executable in dist/. PyInstaller builds for the
# system it runs on, so build on Linux for a Linux release, on Windows for a
# Windows release, and so on.
#
# Started without arguments (as a game platform does), the game uses the
# config.json next to the executable, or the copy bundled below.

a = Analysis(
    ['pac-man.py'],
    # Our modules are imported as `controllers`, `models`, `utils`, `views`.
    pathex=['src'],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('README.md', '.'),
    ],
    # The assigned A-Maze-ing package (imported as `mazegenerator`).
    hiddenimports=['mazegenerator'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'pydoc', 'mypy', 'flake8'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PacMan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # False hides the terminal window on Windows and macOS.
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
