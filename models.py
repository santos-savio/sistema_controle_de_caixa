from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from appdirs import user_data_dir

db = SQLAlchemy()
migrate = Migrate()

def get_database_path():
    """Retorna o caminho do banco de dados no AppData do usuário"""
    app_name = "controle_caixa"
    data_dir = user_data_dir(app_name, appauthor=False)
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "controle_caixa.db")

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com transações
    transacoes = db.relationship('Transacao', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com transações
    transacoes = db.relationship('Transacao', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'

class ProdutoServico(db.Model):
    __tablename__ = 'produtos_servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com transações
    transacoes = db.relationship('Transacao', backref='produto_servico', lazy=True)
    
    def __repr__(self):
        return f'<ProdutoServico {self.nome}>'

class Transacao(db.Model):
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    produto_servico_id = db.Column(db.Integer, db.ForeignKey('produtos_servicos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_transacao = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Transacao {self.id} - {self.valor}>'

class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    campo_nome = db.Column(db.String(50), nullable=False, unique=True)
    visivel = db.Column(db.Boolean, default=True)
    obrigatorio = db.Column(db.Boolean, default=False)
    ordem = db.Column(db.Integer, default=0)
    tipo_campo = db.Column(db.String(20), default='text')  # text, number, date, select
    
    def __repr__(self):
        return f'<Configuracao {self.campo_nome}>'
