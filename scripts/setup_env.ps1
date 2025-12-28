# PowerShell helper to create venv and install requirements
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Virtualenv created and requirements installed. Activate with: . ./.venv/Scripts/Activate.ps1"