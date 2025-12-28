from app import create_app
from app.models import db, Client, Product

def init_database():
    """Inicializa o banco de dados com dados básicos"""
    app = create_app()
    
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        # Verificar se já existem produtos básicos
        if not Product.query.first():
            produtos = [
                Product(name='Consulta', price=50.00),
                Product(name='Serviço Básico', price=100.00),
                Product(name='Serviço Premium', price=200.00),
            ]
            for p in produtos:
                db.session.add(p)
        
        db.session.commit()
        print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_database()
