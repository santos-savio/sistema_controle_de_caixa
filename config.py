import os
 
 
class Config:
    """Application configuration.

    By default the SQLite DB file is stored in the user's local app data directory.
    """
    APP_NAME = "Controle_de_caixa"
    APP_AUTHOR = None

    DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), APP_NAME)
    os.makedirs(DATA_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATA_DIR, 'caixa.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-me-in-prod')
