# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Sistema de Controle de Caixa
"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Get the directory where the spec file is located
project_root = os.path.abspath(os.getcwd())

# Collect all necessary data files
datas = []

# Collect templates and static files for Flask
templates_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')

if os.path.exists(templates_dir):
    datas.append((templates_dir, 'templates'))

if os.path.exists(static_dir):
    datas.append((static_dir, 'static'))

# Include logo.ico for window icon and runtime access
logo_path = os.path.join(project_root, 'logo.ico')
if os.path.exists(logo_path):
    datas.append((logo_path, '.'))  # Include in runtime data
else:
    logo_path = None


# Comprehensive hidden imports for Flask application and launcher
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
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'webbrowser',
    'threading',
    'subprocess',
    'psutil',
    'socket',
    'pathlib',
    'os',
    'sys',
    'time',
    'signal',
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
    ['launcher.py'],
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
    name='controle_de_caixa',
    icon=logo_path,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
