# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Sistema de Controle de Caixa Database Initializer
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Diretório raiz do projeto
project_root = os.path.abspath(os.getcwd())

# Coletar arquivos de dados do app
datas = []
try:
    # Templates e arquivos estáticos
    if os.path.exists('templates'):
        datas.append(('templates', 'templates'))
    if os.path.exists('static'):
        datas.append(('static', 'static'))
    
    # Arquivos de configuração
    config_files = ['config.py', '.env']
    for config_file in config_files:
        if os.path.exists(config_file):
            datas.append((config_file, '.'))
    
    # Coletar arquivos de dados do app
    app_datas = collect_data_files('app')
    datas.extend(app_datas)
    
except Exception as e:
    print(f"Aviso: Não foi possível coletar alguns arquivos de dados: {e}")

# Hidden imports para garantir que todos os módulos sejam incluídos
hiddenimports = []
try:
    # Módulos Flask e SQLAlchemy
    hiddenimports.extend(collect_submodules('flask'))
    hiddenimports.extend(collect_submodules('sqlalchemy'))
    hiddenimports.extend(collect_submodules('werkzeug'))
    
    # Módulos da aplicação
    hiddenimports.extend(collect_submodules('app'))
    
    # Módulos específicos que podem faltar
    hiddenimports.extend([
        'flask_sqlalchemy',
        'flask_migrate',
        'sqlite3',
        'click',
        'jinja2',
        'itsdangerous',
        'markupsafe',
        'werkzeug.debug',
        'werkzeug.local',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.orm',
        'appdirs',
        'python_dotenv',
        'dotenv'
    ])
    
except Exception as e:
    print(f"Aviso: Não foi possível coletar alguns módulos ocultos: {e}")

# Remover duplicatas
hiddenimports = list(set(hiddenimports))

# Análise do arquivo principal
a = Analysis(
    ['init_db.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tkinter',
        'unittest',
        'test',
        'tests'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remover arquivos desnecessários
a.binaries = [b for b in a.binaries if not b[0].startswith('tkinter')]
a.datas = [d for d in a.datas if not any(exclude in d[0] for exclude in ['test', 'tests', '__pycache__'])]

# Configuração do executável
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='init_database',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Necessário para ver a saída do console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
