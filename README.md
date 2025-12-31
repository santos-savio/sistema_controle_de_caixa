# Sistema de Controle de Caixa

Um sistema completo de controle de caixa desenvolvido em Python com Flask, ideal para pequenos e médios negócios gerenciarem vendas, clientes e produtos.

## 🚀 Funcionalidades

### 💰 Registro de Vendas
- **Múltiplos produtos por venda** - Adicione quantos itens precisar
- **Edição individual** - Modifique quantidade e preço de cada produto
- **Cálculos automáticos** - Subtotais e total geral calculados instantaneamente
- **Múltiplas formas de pagamento** - Dinheiro, cartão, PIX, etc.
- **Gestão de clientes** - Cadastro e busca rápida de clientes

### 📦 Gestão de Produtos
- **Cadastro de produtos** - Adicione produtos com preços
- **Produtos personalizados** - Venda itens não catalogados
- **Preços dinâmicos** - Altere preços durante a venda

### 🎯 Interface Intuitiva
- **Design responsivo** - Funciona em computadores e tablets
- **Modais de edição** - Interface amigável para alterações
- **Validações em tempo real** - Evita erros de preenchimento
- **Cores informativas** - Indicadores visuais de status

### 🛠️ Administração
- **Relatórios de vendas** - Acompanhe o desempenho
- **Configurações personalizáveis** - Adapte o sistema ao seu negócio
- **Launcher dedicado** - Inicialização fácil com interface gráfica

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/santos-savio/sistema_controle_de_caixa.git
cd sistema_controle_de_caixa
```

### 2. Crie um ambiente virtual
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Inicialize o banco de dados
```bash
python init_db.py
```

## 🚀 Execução

### Usando o Launcher (Recomendado)
```bash
python launcher_improved.py
```

### Execução direta do servidor
```bash
python app.py
```

O sistema estará disponível em `http://127.0.0.1:5001`

## 📁 Estrutura do Projeto

```
sistema_controle_de_caixa/
├── app.py                 # Aplicação Flask principal
├── launcher_improved.py    # Interface gráfica para iniciar o sistema
├── init_db.py           # Script de inicialização do banco
├── reset_database.py     # Script para resetar o banco
├── config.py            # Configurações da aplicação
├── requirements.txt      # Dependências Python
├── logo.ico            # Ícone do aplicativo
├── templates/          # Templates HTML
│   ├── index.html     # Página principal de vendas
│   ├── relatorios.html # Página de relatórios
│   └── configuracoes.html # Página de configurações
├── static/            # Arquivos estáticos
│   ├── css/          # Estilos CSS
│   ├── js/           # Scripts JavaScript
│   └── images/       # Imagens
└── database.db       # Banco de dados SQLite
```

## 🎯 Como Usar

### 1. Iniciar o Sistema
- Execute `python launcher_improved.py`
- Clique em "🌐 Abrir Página Web"
- O sistema abrirá automaticamente no navegador

### 2. Registrar uma Venda
1. **Selecione o cliente** (opcional)
2. **Adicione produtos**:
   - Escolha da lista ou selecione "Outro"
   - Clique em "Adicionar"
   - Repita para múltiplos itens
3. **Edite se necessário**:
   - Clique em "Editar" em qualquer produto
   - Altere quantidade ou preço
4. **Defina o pagamento**:
   - Escolha a forma de pagamento
   - Adicione múltiplos métodos se necessário
5. **Salve a venda**

### 3. Gerenciar Produtos
- Acesse a página "Admin" para cadastrar produtos
- Defina nome e preço para cada item

### 4. Visualizar Relatórios
- Acesse "Admin" para ver relatórios de vendas
- Filtre por período e visualize totais

## 🔧 Configurações

### Configurações do Sistema
- Acesse "Configurações" no menu superior
- Personalize campos visíveis no formulário
- Configure métodos de pagamento

### Configurações do Servidor
- Host: `127.0.0.1` (localhost)
- Porta: `5001` (automática se ocupada)

## 📦 Tecnologias Utilizadas

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados**: SQLite
- **Interface Gráfica**: Tkinter
- **Deployment**: PyInstaller (opcional)

## 🔒 Segurança

- Validação de entrada de dados
- Proteção contra SQL Injection
- Sanitização de dados do usuário
- Ambiente isolado (venv)

## 🐛 Troubleshooting

### Problemas Comuns

**Porta já em uso**
- O sistema tenta automaticamente portas subsequentes (5002, 5003...)
- Verifique se outro processo está usando a porta

**Erro de permissão**
- Execute como administrador se necessário
- Verifique permissões da pasta do projeto

**Banco de dados corrompido**
- Execute `python reset_database.py`
- Isso limpará todos os dados, use com cuidado

### Logs
- Logs do launcher: `launcher.log`
- Logs da aplicação: Console

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Sávio Gabriel**
- GitHub: [github.com/santos-savio](https://github.com/santos-savio)
- Desenvolvedor Python e entusiasta de sistemas de gestão

## 🙏 Agradecimentos

- Comunidade Python pela excelente documentação
- Framework Flask pela simplicidade e poder
- Contribuidores de código aberto que inspiram este projeto

---

**Sistema de Controle de Caixa** - Simplificando a gestão do seu negócio! 🚀
