from flask import Blueprint, render_template, request, jsonify
from app.models import db, Client, Product, Transaction, TransactionItem
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal com formulário de registro"""
    # Obter produtos/serviços ativos
    produtos = Product.query.filter_by(active=True).all()
    
    return render_template('index.html', produtos=produtos)

@main_bp.route('/api/clients')
def api_clients():
    """API para busca de clientes"""
    query = request.args.get('q', '')
    
    if query:
        clients = Client.query.filter(
            Client.name.contains(query)
        ).limit(10).all()
    else:
        clients = Client.query.limit(10).all()
    
    return jsonify([{'id': c.id, 'name': c.name} for c in clients])

@main_bp.route('/api/transaction', methods=['POST'])
def api_salvar_transaction():
    """API para salvar nova transação"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not data.get('items') or not data.get('total'):
            return jsonify({'error': 'Campos obrigatórios faltando'}), 400
        
        # Criar nova transação
        transaction = Transaction(
            client_id=data.get('client_id'),
            total=float(data['total']),
            notes=data.get('notes', ''),
            date=datetime.utcnow()
        )
        
        db.session.add(transaction)
        db.session.flush()  # Obter ID da transação
        
        # Adicionar itens
        for item_data in data['items']:
            item = TransactionItem(
                transaction_id=transaction.id,
                product_id=item_data.get('product_id'),
                description=item_data.get('description', ''),
                qty=item_data.get('qty', 1),
                unit_price=item_data.get('unit_price'),
                subtotal=item_data.get('subtotal')
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({'success': True, 'transaction_id': transaction.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
