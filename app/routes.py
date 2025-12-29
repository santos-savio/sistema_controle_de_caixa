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

@main_bp.route('/configuracoes')
def configuracoes():
    """Página de configuração dos campos"""
    return render_template('configuracoes.html')

@main_bp.route('/resumo')
def resumo():
    """Página de resumo visual"""
    return render_template('resumo.html')

@main_bp.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html')

@main_bp.route('/api/resumo')
def api_resumo():
    """API para dados do resumo"""
    try:
        # Estatísticas básicas
        total_transacoes = Transaction.query.count()
        total_valor = db.session.query(db.func.sum(Transaction.total)).scalar() or 0
        total_clientes = Client.query.count()
        total_produtos = Product.query.filter_by(active=True).count()
        
        # Transações recentes
        transacoes_recentes = Transaction.query.order_by(
            Transaction.date.desc()
        ).limit(5).all()
        
        recentes = []
        for t in transacoes_recentes:
            recentes.append({
                'cliente': t.client.name if t.client else 'Não informado',
                'produto': t.items[0].product.name if t.items and t.items[0].product else 'N/A',
                'valor': float(t.total),
                'data': t.date.strftime('%d/%m/%Y %H:%M')
            })
        
        return jsonify({
            'total_transacoes': total_transacoes,
            'total_valor': float(total_valor),
            'total_clientes': total_clientes,
            'total_produtos': total_produtos,
            'transacoes_recentes': recentes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@main_bp.route('/api/produtos')
def api_produtos():
    """API para lista de produtos"""
    produtos = Product.query.filter_by(active=True).all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': float(p.price)} for p in produtos])

@main_bp.route('/api/produtos', methods=['POST'])
def api_criar_produto():
    """API para criar novo produto"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('price'):
            return jsonify({'error': 'Nome e preço são obrigatórios'}), 400
        
        produto = Product(
            name=data['name'],
            price=float(data['price']),
            active=True
        )
        
        db.session.add(produto)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'produto': {
                'id': produto.id,
                'name': produto.name,
                'price': float(produto.price)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def api_remover_produto(produto_id):
    """API para remover produto (desativar)"""
    try:
        produto = Product.query.get_or_404(produto_id)
        
        # Verificar se há transações usando este produto
        tem_transacoes = TransactionItem.query.filter_by(product_id=produto_id).first()
        
        if tem_transacoes:
            # Se foi utilizado, apenas desativar
            produto.active = False
            db.session.commit()
            return jsonify({'success': True, 'message': 'Produto desativado com sucesso'})
        else:
            # Se não foi utilizado, pode remover completamente
            db.session.delete(produto)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Produto removido com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/relatorios')
def api_relatorios():
    """API para gerar relatórios"""
    try:
        # Obter parâmetros de data
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        cliente = request.args.get('cliente')
        produto_id = request.args.get('produto')
        
        # Construir query
        query = Transaction.query.join(TransactionItem).join(Product)
        
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Transaction.date >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Transaction.date <= data_fim_dt)
        
        if cliente:
            query = query.join(Client).filter(Client.name.contains(cliente))
        
        if produto_id:
            query = query.filter(Product.id == produto_id)
        
        transactions = query.order_by(Transaction.date.desc()).all()
        
        # Formatar dados
        dados = []
        for t in transactions:
            dados.append({
                'id': t.id,
                'cliente': t.client.name if t.client else 'Não informado',
                'produto': t.items[0].product.name if t.items and t.items[0].product else 'N/A',
                'valor': float(t.total),
                'data': t.date.strftime('%d/%m/%Y %H:%M'),
                'observacoes': t.notes or ''
            })
        
        return jsonify({'dados': dados})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
