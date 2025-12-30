"""Script para resetar completamente o banco de dados"""

import os
import sqlite3
from app import create_app
from app.models import db

def reset_database():
    """Reseta completamente o banco de dados"""
    app = create_app()
    
    with app.app_context():
        # Obter caminho do banco de dados
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print(f"Resetando banco de dados: {db_path}")
        
        # Fechar todas as conexões
        db.session.close_all()
        
        # Remover arquivo do banco
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Banco de dados removido")
        
        # Criar todas as tabelas novas
        db.create_all()
        print("Novo banco de dados criado")
        
        # Importar e executar scripts de inicialização
        from init_system_config import init_system_config
        from init_payment_methods import init_payment_methods
        
        print("\nInicializando configurações do sistema...")
        init_system_config()
        
        print("\nInicializando métodos de pagamento...")
        init_payment_methods()
        
        print("\n✅ Banco de dados resetado com sucesso!")
        print("📋 Configurações iniciais:")
        print("   - PIN padrão: 1234")
        print("   - Métodos de pagamento: Dinheiro, PIX, Cartão de Crédito, Cartão de Débito")

if __name__ == '__main__':
    reset_database()
