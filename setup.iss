; Script de Instalação para Sistema de Controle de Caixa
; Desenvolvido por Sávio Gabriel
; Licença MIT

#define MyAppName "Sistema de Controle de Caixa"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sávio Gabriel"
#define MyAppURL "https://github.com/santos-savio/sistema_controle_de_caixa"
#define MyAppExeName "sistema_controle_de_caixa.exe"
#define MyAppAssocName "Controle de Caixa"
#define MyAssocName "savio.dev.br"

[Setup]
AppId={{35D8A5A-4E3F-4A5B-9B5A-2F5E5E5E5E5E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=Controle_de_Caixa-Setup
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; WizardImageFile=logo.ico
; WizardImageStretch=no
ShowLanguageDialog=yes
LanguageDetectionMethod=locale

; Variáveis de diretório
#define DataDir "{app}"
#define TempDir "{tmp}"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Criar atalho na barra de inicialização rápida"; GroupDescription: "Atalhos"; Flags: unchecked

[Files]
; Executável principal (único)
Source: "dist\SistemaControleCaixa.exe"; DestDir: "{app}"; DestName: "launcher.exe"; Flags: ignoreversion

; Arquivos do sistema (templates, static, etc.)
Source: "templates\*"; DestDir: "{app}\templates"; Flags: recursesubdirs createallsubdirs
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; Arquivos da pasta app (se existirem)
Source: "app\*"; DestDir: "{app}\app"; Flags: recursesubdirs createallsubdirs ignoreversion

; Scripts (se existirem)
Source: "scripts\*"; DestDir: "{app}\scripts"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\launcher.exe"; IconFilename: "{app}\logo.ico"; Comment: "Sistema de Controle de Caixa"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\launcher.exe"; Tasks: desktopicon; IconFilename: "{app}\logo.ico"; Comment: "Sistema de Controle de Caixa"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\launcher.exe"; Tasks: quicklaunchicon; IconFilename: "{app}\logo.ico"; Comment: "Sistema de Controle de Caixa"

[Run]
; Executar inicialização do sistema após instalação
Filename: "{app}\launcher.exe"; Parameters: "--init-only"; Description: "Inicializando sistema"; Flags: runhidden waituntilterminated

[Registry]
; Registrar associação de arquivos (opcional)
Root: HKCR; Subkey: ".scaixa"; ValueType: string; ValueName: ""; ValueData: "{#MyAssocName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: ".scaixa"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-sistema-caixa"; Flags: uninsdeletekey
Root: HKCR; Subkey: "{#MyAssocName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\launcher.exe"" ""%1"""; Flags: uninsdeletekey

; Informações do aplicativo no Adicionar/Remover Programas
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#MyAppURL}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "HelpLink"; ValueData: "{#MyAppURL}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\logo.ico"

[UninstallDelete]
; Remover arquivos temporários (NÃO remover o banco de dados aqui)
Type: filesandordirs; Name: "{app}\SistemaControleCaixa.log"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\app\__pycache__"

[UninstallRun]
; Não executar nada durante desinstalação (silencioso)

[Code]
// Funções em Pascal para personalização da instalação

// Função GetAppId removida - AppId definido diretamente em [Setup]

// Função CheckPythonInstalled removida - Python não é mais verificado
// A aplicação cuidará das dependências necessárias

function InitializeSetup(): Boolean;
var
  UninstallKey, UninstallKey64: String;
  Has32Bit, Has64Bit: Boolean;
begin
  // Verificar instalações existentes em ambas as arquiteturas
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}';
  UninstallKey64 := 'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}';
  
  Has32Bit := RegKeyExists(HKEY_LOCAL_MACHINE, UninstallKey);
  Has64Bit := RegKeyExists(HKEY_LOCAL_MACHINE, UninstallKey64);
  
  // Se encontrar alguma instalação, perguntar sobre desinstalação
  if Has32Bit or Has64Bit then
  begin
    if Has32Bit and Has64Bit then
      MsgBox('Atenção: Foram encontradas múltiplas instalações do Sistema de Controle de Caixa.' + #13#10 + 
             'Isso pode ter causado a duplicação no registro.' + #13#10 + 
             'Deseja continuar com a instalação (será feita uma limpeza)?', 
             mbConfirmation, MB_YESNO)
    else
      MsgBox('O Sistema de Controle de Caixa já está instalado.' + #13#10 + 'Deseja desinstalar a versão anterior e continuar?', 
             mbConfirmation, MB_YESNO);
             
    if MsgBox('Deseja limpar todos os registros anteriores antes de continuar?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Limpar registros existentes
      if Has32Bit then
      begin
        if not RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, UninstallKey) then
          MsgBox('Aviso: Não foi possível remover completamente o registro 32-bit.', mbInformation, MB_OK);
      end;
      
      if Has64Bit then
      begin
        if not RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, UninstallKey64) then
          MsgBox('Aviso: Não foi possível remover completamente o registro 64-bit.', mbInformation, MB_OK);
      end;
      
      // Limpar também possíveis chaves com nome diferente
      if RegKeyExists(HKEY_LOCAL_MACHINE, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa') then
        RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa');
        
      if RegKeyExists(HKEY_LOCAL_MACHINE, 'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa') then
        RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa');
    end
    else
    begin
      Result := False;
      Exit;
    end;
  end;
  
  // Verificar permissões de administrador
  if not IsAdminLoggedOn then
  begin
    MsgBox('É recomendado executar este instalador como administrador para garantir a instalação correta.', 
            mbInformation, MB_OK);
  end;
  
  Result := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Página de finalização - sem verificação de banco de dados
  if CurPageID = wpFinished then
  begin
    // A aplicação irá cuidar da inicialização do banco de dados
    // Não fazer nada aqui
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // Pular página de seleção de componentes (não temos componentes opcionais)
  Result := (PageID = wpSelectComponents);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Mensagem de desinstalação
        MsgBox('Desinstalando Sistema de Controle de Caixa...' + #13#10 + 
               'Seus dados serão preservados se você desejar mantê-los.', 
               mbInformation, MB_OK);
      end;
    usPostUninstall:
      begin
        // Remover TODAS as chaves do registro do Windows (32-bit e 64-bit)
        if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa') then
        begin
          if not RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa') then
            MsgBox('Aviso: Não foi possível remover completamente a chave do registro 64-bit.', mbInformation, MB_OK);
        end;
        
        if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa') then
        begin
          if not RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Sistema de Controle de Caixa') then
            MsgBox('Aviso: Não foi possível remover completamente a chave do registro 32-bit.', mbInformation, MB_OK);
        end;
        
        // Remover também chaves com AppId
        if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}') then
        begin
          if not RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}') then
            MsgBox('Aviso: Não foi possível remover completamente a chave do registro 64-bit (AppId).', mbInformation, MB_OK);
        end;
        
        if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}') then
        begin
          if not RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}') then
            MsgBox('Aviso: Não foi possível remover completamente a chave do registro 32-bit (AppId).', mbInformation, MB_OK);
        end;
        
        // Perguntar sobre exclusão de dados
        if MsgBox('Deseja remover todos os dados do sistema (vendas, clientes, produtos, etc.)?' + #13#10 + 
                  'Clique em Não para preservar os dados para uma futura instalação.' + #13#10 + 
                  'AVISO: Esta ação não poderá ser desfeita!', 
                  mbConfirmation, MB_YESNO) = IDYES then
        begin
          // Remover banco de dados principal
          if FileExists(ExpandConstant('{app}\database.db')) then
          begin
            if not DeleteFile(ExpandConstant('{app}\database.db')) then
              MsgBox('Aviso: Não foi possível remover o arquivo do banco de dados.', mbInformation, MB_OK);
          end;
          
          // Remover diretório de dados se existir
          if DirExists(ExpandConstant('{app}\data')) then
          begin
            if not DelTree(ExpandConstant('{app}\data'), True, True, True) then
              MsgBox('Aviso: Não foi possível remover completamente o diretório de dados.', mbInformation, MB_OK);
          end;
          
          // Remover outros possíveis arquivos de dados
          if FileExists(ExpandConstant('{app}\database.db-journal')) then
            DeleteFile(ExpandConstant('{app}\database.db-journal'));
            
          if FileExists(ExpandConstant('{app}\database.db-wal')) then
            DeleteFile(ExpandConstant('{app}\database.db-wal'));
            
          if FileExists(ExpandConstant('{app}\database.db-shm')) then
            DeleteFile(ExpandConstant('{app}\database.db-shm'));
        end
        else
        begin
          // Se usuário optou por preservar dados, mostrar mensagem
          MsgBox('Seus dados serão preservados na pasta de instalação.' + #13#10 + 
                 'Eles estarão disponíveis se você reinstalar o sistema futuramente.', 
                 mbInformation, MB_OK);
        end;
      end;
  end;
end;

