Issues planejadas — MVP Caixa
Labels sugeridos: backend, frontend, packaging, tests, enhancement

Epic A — Core & DB
1. Inicializar banco e estrutura de dados
Arquivos: app/db.py, db/init_db.py
Estimativa: 6h
AC: DB criado em %LOCALAPPDATA%\AppName\cash.db com WAL ativado.
2. Modelos ORM (Client/Product/Transaction)
Arquivo: app/models.py
Estimativa: 8h
AC: Models implementados + testes unitários.
3. Migrações e script de upgrade
Arquivos: migrations/, app/migrations.py
Estimativa: 4h
AC: flask db upgrade aplica esquema sem erro.
4. Backups rotativos e utilitário de restore
Arquivo: app/db_backup.py
Estimativa: 4h
AC: Backup manual e script agendável funcionando.
Epic B — UI / Webview
5. Wrapper e inicialização do webview
Arquivo: main.py
Estimativa: 6h
AC: App inicia pywebview sem console visível.
6. Template principal (index)
Arquivos: templates/index.html, static/css/style.css
Estimativa: 6h
AC: Layout renderiza e é responsivo.
7. JS de interação UI ↔ API
Arquivo: static/js/app.js
Estimativa: 8h
AC: Autocomplete, add/remove produto, cálculo total e save OK.
8. Assets e ícones
Arquivo: assets/icon.ico
Estimativa: 2h
AC: Ícone aparece no exe e atalhos.
Epic C — Funcionalidades
9. Busca / Autocomplete de cliente + remoção
Arquivos: app/api/clients.py, static/js/app.js
Estimativa: 6h
AC: Busca por substring e botão remover limpa UI.
10. Listbox de produtos/serviços
Arquivos: app/api/products.py, templates/partials/product_list.html
Estimativa: 6h
AC: Seleção múltipla soma corretamente.
11. Configurar campos visíveis (modal)
Arquivos: templates/config.html, app/api/settings.py
Estimativa: 6h
AC: Config persistida e reflete na UI.
12. Resumo “PIN” (painel fixo)
Arquivos: app/api/auth.py, templates/summary.html
Estimativa: 6h
AC: PIN requer hash válido para abrir resumo.
Epic D — Relatórios & Export
13. Relatório por intervalo de datas (export)
Arquivo: app/api/reports.py, app/utils/export.py
Estimativa: 8h
AC: Export CSV/XLSX/PDF válido.
14. Página de export + filtros UI
Arquivos: templates/report.html, static/js/report.js
Estimativa: 4h
AC: Filtros aplicam e retornam arquivo.
Epic E — Empacotamento, Tests & Release
15. Script PyInstaller + spec
Arquivos: pyinstaller.spec, scripts/build_exe.ps1
Estimativa: 6h
AC: .exe sem console e com ícone.
16. Instaler Inno Setup
Arquivo: installer/installer.iss
Estimativa: 4h
AC: Instalador cria atalho e funciona em VM limpa.
17. Suíte de testes automatizados
Arquivos: tests/*, ci/workflows.yml
Estimativa: 8h
AC: Testes críticos no CI.