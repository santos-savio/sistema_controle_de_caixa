"""Script para inicializar o banco de dados com a tabela system_config"""

from app import create_app
from app.models import db, SystemConfig

def init_system_config():
    """Inicializa a tabela system_config se não existir"""
    app = create_app()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se já existe um PIN configurado
        pin_existente = SystemConfig.get_value('admin_pin')
        
        if not pin_existente:
            # Definir PIN padrão
            SystemConfig.set_value('admin_pin', '1234', 'PIN de acesso ao painel administrativo')
            print("PIN padrão '1234' configurado")
        else:
            print(f"PIN já configurado: {pin_existente}")
        
        print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_system_config()
