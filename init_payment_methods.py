"""Script para inicializar métodos de pagamento padrão"""

from app import create_app
from app.models import db, PaymentMethod

def init_payment_methods():
    """Inicializa métodos de pagamento padrão se não existirem"""
    app = create_app()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Métodos de pagamento padrão
        default_methods = [
            {
                'name': 'Dinheiro',
                'code': 'dinheiro',
                'description': 'Pagamento em dinheiro',
                'color': '#28a745'  # verde
            },
            {
                'name': 'PIX',
                'code': 'pix',
                'description': 'Pagamento via PIX',
                'color': '#007bff'  # azul
            },
            {
                'name': 'Cartão de Crédito',
                'code': 'credito',
                'description': 'Pagamento com cartão de crédito',
                'color': '#fd7e14'  # laranja
            },
            {
                'name': 'Cartão de Débito',
                'code': 'debito',
                'description': 'Pagamento com cartão de débito',
                'color': '#6f42c1'  # roxo
            }
        ]
        
        created_count = 0
        for method_data in default_methods:
            # Verificar se já existe
            existing = PaymentMethod.query.filter_by(code=method_data['code']).first()
            
            if not existing:
                method = PaymentMethod(**method_data)
                db.session.add(method)
                created_count += 1
                print(f"Método de pagamento criado: {method.name}")
            else:
                print(f"Método de pagamento já existe: {method.name}")
        
        db.session.commit()
        
        if created_count > 0:
            print(f"\n{created_count} métodos de pagamento criados com sucesso!")
        else:
            print("\nTodos os métodos de pagamento padrão já existem.")
        
        print("\nMétodos de pagamento disponíveis:")
        methods = PaymentMethod.get_active_methods()
        for method in methods:
            print(f"  - {method.name} ({method.code})")

if __name__ == '__main__':
    init_payment_methods()
