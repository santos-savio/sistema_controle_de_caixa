@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: Script de Build Automatizado - Sistema de Controle de Caixa
:: Desenvolvido por Sávio Gabriel
:: ============================================================================

echo.
echo ====================================================================
echo    Sistema de Controle de Caixa - Build Automatizado
echo ====================================================================
echo.

:: Verificar se estamos no diretório correto
if not exist "launcher.py" (
    echo [ERRO] launcher.py nao encontrado. Execute este script na pasta raiz do projeto.
    pause
    exit /b 1
)

if not exist "init_db.py" (
    echo [ERRO] init_db.py nao encontrado. Execute este script na pasta raiz do projeto.
    pause
    exit /b 1
)

if not exist "setup.iss" (
    echo [ERRO] setup.iss nao encontrado. Execute este script na pasta raiz do projeto.
    pause
    exit /b 1
)

:: Verificar se o ambiente virtual existe
if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado. Execute 'python -m venv .venv' primeiro.
    pause
    exit /b 1
)

:: Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

:: Verificar se PyInstaller está instalado
echo [1/5] Verificando dependencias...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando PyInstaller...
    pip install pyinstaller
)

:: Verificar se Inno Setup está disponível
echo [2/5] Verificando Inno Setup...
where iscc >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Inno Setup (iscc.exe) nao encontrado no PATH.
    echo        Baixe e instale em: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

:: Limpar builds anteriores
echo [3/5] Limpando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" (
    echo [INFO] Arquivos .spec encontrados, mantendo...
) else (
    echo [INFO] Nenhum build anterior encontrado.
)

:: Compilar launcher
echo [4/5] Compilando launcher.exe...
echo.
echo --------------------------------------------------------------------
echo    Compilando: launcher.py -> launcher.exe
echo --------------------------------------------------------------------
pyinstaller launcher.spec --clean --noconfirm

if errorlevel 1 (
    echo [ERRO] Falha ao compilar launcher.exe
    pause
    exit /b 1
)

if not exist "dist\controle_de_caixa.exe" (
    echo [ERRO] controle_de_caixa.exe nao foi gerado
    pause
    exit /b 1
)

echo [SUCESSO] controle_de_caixa.exe compilado com sucesso!

:: Compilar init_database
echo.
echo [4/5] Compilando init_database.exe...
echo --------------------------------------------------------------------
echo    Compilando: init_db.py -> init_database.exe
echo --------------------------------------------------------------------
pyinstaller init_db.spec --clean --noconfirm

if errorlevel 1 (
    echo [ERRO] Falha ao compilar init_database.exe
    pause
    exit /b 1
)

if not exist "dist\init_database.exe" (
    echo [ERRO] init_database.exe nao foi gerado
    pause
    exit /b 1
)

echo [SUCESSO] init_database.exe compilado com sucesso!

:: Compilar instalador com Inno Setup
echo.
echo [5/5] Compilando instalador com Inno Setup...
echo --------------------------------------------------------------------
echo    Compilando: setup.iss -> Controle_de_Caixa-Setup.exe
echo --------------------------------------------------------------------
iscc setup.iss

if errorlevel 1 (
    echo [ERRO] Falha ao compilar o instalador
    pause
    exit /b 1
)

:: Verificar se o instalador foi criado
if not exist "dist\Controle_de_Caixa-Setup.exe" (
    echo [ERRO] Controle_de_Caixa-Setup.exe nao foi gerado
    pause
    exit /b 1
)

:: Build concluído com sucesso
echo.
echo ====================================================================
echo    BUILD CONCLUIDO COM SUCESSO!
echo ====================================================================
echo.
echo Arquivos gerados:
echo   - dist\controle_de_caixa.exe        (Launcher principal)
echo   - dist\init_database.exe         (Inicializador do banco)
echo   - dist\Controle_de_Caixa-Setup.exe (Instalador completo)
echo.
echo Tamanhos dos arquivos:
for %%f in ("dist\*.exe") do (
    echo   - %%f: %%~zf bytes
)
echo.
echo O instalador esta pronto para distribuicao!
echo.

:: Perguntar se quer executar o instalador
set /p execute="Deseja executar o instalador agora? (S/N): "
if /i "!execute!"=="S" (
    echo.
    echo [INFO] Executando o instalador...
    start "" "dist\Controle_de_Caixa-Setup.exe"
) else (
    echo.
    echo [INFO] Build concluido. Execute 'dist\Controle_de_Caixa-Setup.exe' para instalar.
)

echo.
pause
