# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Diretório raiz do projeto
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)

# Caminho para o logo
logo_path = os.path.join(project_root, 'logo.ico')

# Coletar arquivos de dados do app
datas = []
try:
    # Templates e arquivos estáticos
    if os.path.exists('templates'):
        templates_data = collect_data_files('templates')
        datas.extend(templates_data)
    
    # Arquivos da pasta app
    app_data = collect_data_files('app')
    datas.extend(app_data)
    
    # Arquivos de configuração
    config_files = ['config.py', '.env']
    for config_file in config_files:
        if os.path.exists(config_file):
            datas.append((config_file, '.'))
    
    # Scripts de inicialização (agora como módulos internos)
    init_scripts = [
        'init_db.py',
        'reset_database.py', 
        'init_payment_methods.py',
        'init_system_config.py'
    ]
    for script in init_scripts:
        if os.path.exists(script):
            datas.append((script, '.'))
    
except Exception as e:
    print(f"Aviso: Não foi possível coletar alguns arquivos de dados: {e}")

# Hidden imports para garantir que todos os módulos sejam incluídos
hiddenimports = [
    # Módulos Flask e SQLAlchemy
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
    
    # Módulos do sistema
    'sqlite3',
    'socket',
    'threading',
    'subprocess',
    'psutil',
    'pathlib',
    'os',
    'sys',
    'time',
    'signal',
    'argparse',
    'logging',
    
    # Módulos específicos que podem faltar
    'appdirs',
    'python_dotenv',
    'dotenv',
    'werkzeug.debug',
    'werkzeug.local',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',
    
    # Módulos da aplicação
    'app',
    'app.db',
    'app.models',
    'app.routes',
    'config',
    
    # Scripts de inicialização
    'init_db',
    'reset_database',
    'init_payment_methods',
    'init_system_config',
    
    # Launcher
    'launcher',
]

# Coletar todos os submódulos
try:
    hiddenimports += collect_submodules('flask')
    hiddenimports += collect_submodules('sqlalchemy')
    hiddenimports += collect_submodules('werkzeug')
    hiddenimports += collect_submodules('app')
except Exception as e:
    print(f"Aviso: Não foi possível coletar alguns submódulos: {e}")

# Remover duplicatas
hiddenimports = list(set(hiddenimports))

# Excluir módulos de desenvolvimento
excludes = [
    'pytest',
    'pytest_flask',
    'unittest',
    'doctest',
    'scipy',
    'PIL',
    'cv2',
    'tkinter',
    'test',
    'tests'
]

# Análise do arquivo principal
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
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
    a.zipfiles,
    a.datas,
    [],
    name='SistemaControleCaixa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Aplicação GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=logo_path,
)
