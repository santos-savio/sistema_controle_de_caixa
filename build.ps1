# ============================================================================
# Script de Build Automatizado - Sistema de Controle de Caixa (PowerShell)
# Desenvolvido por Sávio Gabriel
# ============================================================================

param(
    [switch]$Clean,
    [switch]$SkipTests,
    [switch]$NoPause
)

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "   Sistema de Controle de Caixa - Build Automatizado" -ForegroundColor White
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Função para escrever mensagens coloridas
function Write-Status {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $color = switch ($Type) {
        "INFO" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "SUCCESS" { "Cyan" }
        default { "White" }
    }
    
    Write-Host "[$Type] $Message" -ForegroundColor $color
}

# Verificar se estamos no diretório correto
$requiredFiles = @("launcher.py", "init_db.py", "setup.iss")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Status "ERRO: $file nao encontrado. Execute este script na pasta raiz do projeto." "ERROR"
        if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
        exit 1
    }
}

# Verificar ambiente virtual
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Status "ERRO: Ambiente virtual nao encontrado. Execute 'python -m venv .venv' primeiro." "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

# Ativar ambiente virtual
Write-Status "Ativando ambiente virtual..." "INFO"
& .\.venv\Scripts\Activate.ps1

# Verificar dependências
Write-Status "Verificando dependencias..." "INFO"

# Verificar PyInstaller
try {
    python -c "import PyInstaller" 2>$null
    Write-Status "PyInstaller encontrado" "SUCCESS"
} catch {
    Write-Status "Instalando PyInstaller..." "WARN"
    pip install pyinstaller
}

# Verificar Inno Setup
$innosetup = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $innosetup) {
    Write-Status "ERRO: Inno Setup (iscc.exe) nao encontrado no PATH." "ERROR"
    Write-Status "Baixe e instale em: https://jrsoftware.org/isinfo.php" "INFO"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
} else {
    Write-Status "Inno Setup encontrado: $($innosetup.Source)" "SUCCESS"
}

# Limpar builds anteriores se solicitado
if ($Clean) {
    Write-Status "Limpando builds anteriores..." "INFO"
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
}

# Criar diretório dist se não existir
if (-not (Test-Path "dist")) {
    New-Item -ItemType Directory -Path "dist" | Out-Null
}

# Compilar launcher
Write-Status "Compilando launcher.exe..." "INFO"
Write-Host "--------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "   Compilando: launcher.py -> controle_de_caixa.exe" -ForegroundColor White
Write-Host "--------------------------------------------------------------------" -ForegroundColor Gray

$launcherResult = Start-Process -FilePath "pyinstaller" -ArgumentList "launcher.spec --clean --noconfirm" -Wait -PassThru

if ($launcherResult.ExitCode -ne 0) {
    Write-Status "ERRO: Falha ao compilar controle_de_caixa.exe" "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

# Verificar se o executável foi criado
if (-not (Test-Path "dist\controle_de_caixa.exe")) {
    Write-Status "ERRO: controle_de_caixa.exe nao foi gerado" "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

Write-Status "SUCESSO: controle_de_caixa.exe compilado!" "SUCCESS"

# Compilar init_database
Write-Status "Compilando init_database.exe..." "INFO"
Write-Host "--------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "   Compilando: init_db.py -> init_database.exe" -ForegroundColor White
Write-Host "--------------------------------------------------------------------" -ForegroundColor Gray

$initDbResult = Start-Process -FilePath "pyinstaller" -ArgumentList "init_db.spec --clean --noconfirm" -Wait -PassThru

if ($initDbResult.ExitCode -ne 0) {
    Write-Status "ERRO: Falha ao compilar init_database.exe" "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

# Verificar se o executável foi criado
if (-not (Test-Path "dist\init_database.exe")) {
    Write-Status "ERRO: init_database.exe nao foi gerado" "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

Write-Status "SUCESSO: init_database.exe compilado!" "SUCCESS"

# Compilar instalador com Inno Setup
Write-Status "Compilando instalador com Inno Setup..." "INFO"
Write-Host "--------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "   Compilando: setup.iss -> Controle_de_Caixa-Setup.exe" -ForegroundColor White
Write-Host "--------------------------------------------------------------------" -ForegroundColor Gray

$setupResult = Start-Process -FilePath "iscc" -ArgumentList "setup.iss" -Wait -PassThru

if ($setupResult.ExitCode -ne 0) {
    Write-Status "ERRO: Falha ao compilar o instalador" "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

# Verificar se o instalador foi criado
if (-not (Test-Path "dist\Controle_de_Caixa-Setup.exe")) {
    Write-Status "ERRO: Controle_de_Caixa-Setup.exe nao foi gerado" "ERROR"
    if (-not $NoPause) { Read-Host "Pressione Enter para sair" }
    exit 1
}

# Build concluído com sucesso
Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "   BUILD CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Arquivos gerados:" -ForegroundColor White
$files = Get-ChildItem "dist\*.exe"
foreach ($file in $files) {
    $size = [math]::Round($file.Length / 1MB, 2)
    Write-Host "   - $($file.Name): $size MB" -ForegroundColor Gray
}

Write-Host ""
Write-Status "O instalador esta pronto para distribuicao!" "SUCCESS"

# Perguntar se quer executar o instalador
if (-not $NoPause) {
    $execute = Read-Host "Deseja executar o instalador agora? (S/N)"
    if ($execute -eq "S" -or $execute -eq "s") {
        Write-Status "Executando o instalador..." "INFO"
        Start-Process -FilePath "dist\Controle_de_Caixa-Setup.exe"
    } else {
        Write-Host ""
        Write-Status "Build concluido. Execute 'dist\Controle_de_Caixa-Setup.exe' para instalar." "INFO"
    }
    
    Write-Host ""
    Read-Host "Pressione Enter para sair"
}
