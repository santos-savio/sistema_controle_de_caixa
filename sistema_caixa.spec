# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Sistema de Controle de Caixa

Usage:
    pyinstaller --clean --onefile sistema_caixa.spec
    pyinstaller --clean --onedir sistema_caixa.spec  # For directory build

Notes:
- Entry point: `app.py` (starts Flask app with `create_app()`).
- Includes `templates/` and `static/` folders as data files so Flask can render templates when frozen.
- The SQLite DB file is created in the user's app data directory (via `appdirs`) at runtime. Do NOT bundle the DB inside the exe; it should remain a writable file on disk.
- All Flask extensions and SQLAlchemy are properly included via hidden imports.
- Uses UPX compression for smaller executable size.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Get the directory where the spec file is located
project_root = os.path.abspath(os.getcwd())

# Enhanced data collection with better error handling
def collect_folder(src_dir, target_prefix):
    """Walk a folder and return a list of (src, dest) tuples for datas."""
    results = []
    if not os.path.isdir(src_dir):
        print(f"Warning: {src_dir} not found, skipping...")
        return results
    for root, _, files in os.walk(src_dir):
        for f in files:
            src_path = os.path.join(root, f)
            rel_path = os.path.relpath(src_path, src_dir)
            dest_path = os.path.join(target_prefix, rel_path)
            results.append((src_path, dest_path))
    return results

# Collect all necessary data files
datas = []
# Collect templates and static files
datas += collect_folder(os.path.join(project_root, 'templates'), 'templates')
datas += collect_folder(os.path.join(project_root, 'static'), 'static')

# Include Python files that PyInstaller might miss
python_files = ['config.py', 'init_db.py']
for py_file in python_files:
    src_path = os.path.join(project_root, py_file)
    if os.path.exists(src_path):
        datas.append((src_path, '.'))

# Include icon if it exists
icon_path = os.path.join(project_root, 'logo.ico')
if os.path.exists(icon_path):
    print(f"Found icon: {icon_path}")
else:
    print(f"Warning: Icon not found at {icon_path}")
    icon_path = None

# Comprehensive hidden imports for Flask application
hiddenimports = [
    'appdirs',
    'flask',
    'flask_sqlalchemy',
    'flask_migrate',
    'werkzeug',
    'jinja2',
    'markupsafe',
    'sqlalchemy',
    'click',
    'itsdangerous',
    'blinker',
    'app',
    'app.db',
    'app.models',
    'app.routes',
    'config',
    'init_db',
]

# Include all submodules from the app package
hiddenimports += collect_submodules('app')

# Exclude development/testing modules
excludes = [
    'pytest',
    'pytest_flask',
    'unittest',
    'doctest',
]

a = Analysis(
    ['app.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
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
    name='sistema_caixa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Change to False for GUI-only application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Will be None if icon not found
)

# For directory build (onedir), uncomment the following:
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='sistema_caixa'
# )
