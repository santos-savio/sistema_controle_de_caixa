from flask import Blueprint, render_template, request, jsonify, make_response
from app.models import db, Client, Product, Transaction, TransactionItem, SystemConfig, PaymentMethod, Payment
from datetime import datetime

main_bp = Blueprint('main', __name__)

def _format_dt_local_br(dt: datetime) -> str:
    """Formata datetime (armazenado em UTC) para horário local Brasil (UTC-3).
    Retorna string no formato dd/mm/YYYY HH:MM.
    """
    if not dt:
        return ''
    from datetime import timedelta
    dt_local = dt - timedelta(hours=3)
    return dt_local.strftime('%d/%m/%Y %H:%M')

def _format_dt_br(dt: datetime) -> str:
    """Formata datetime para horário Brasil (UTC-3) sem conversão.
    Retorna string no formato dd/mm/YYYY HH:MM.
    """
    if not dt:
        return ''
    # Assume que já está no fuso correto (sangrias), apenas formata
    return dt.strftime('%d/%m/%Y %H:%M')

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
    """API para dados do resumo - usando mesma lógica de cálculo do relatório"""
    try:
        from sqlalchemy import func
        
        # Estatísticas básicas
        total_transacoes = Transaction.query.count()
        
        # Saldo atual do caixa (apenas vendas, sem descontar sangrias)
        saldo_atual = db.session.query(func.sum(Transaction.total)).filter(Transaction.total > 0).scalar() or 0
        
        # Total de vendas (apenas transações positivas)
        total_vendas = db.session.query(func.sum(Transaction.total)).filter(Transaction.total > 0).scalar() or 0
        
        # Total de sangrias (apenas transações negativas)
        total_sangrias = db.session.query(func.sum(Transaction.total)).filter(Transaction.total < 0).scalar() or 0
        
        total_clientes = Client.query.count()
        total_produtos = Product.query.filter_by(active=True).count()
        
        # Transações recentes (incluindo sangrias)
        transacoes_recentes = Transaction.query.order_by(
            Transaction.date.desc()
        ).limit(5).all()
        
        recentes = []
        for t in transacoes_recentes:
            # Verificar se é sangria
            if t.notes and (t.notes.startswith('SANGRIA:') or t.notes.startswith('RETIRADA:')):
                recentes.append({
                    'cliente': 'SANGRIA',
                    'produto': 'Retirada de Caixa',
                    'valor': float(t.total),
                    'data': _format_dt_br(t.date),  # Sangrias já em horário local
                    'tipo': 'sangria'
                })
            else:
                produto_nome = 'N/A'
                if t.items and len(t.items) > 0:
                    if t.items[0].product:
                        produto_nome = t.items[0].product.name
                    elif t.items[0].description:
                        produto_nome = t.items[0].description
                
                recentes.append({
                    'cliente': t.client.name if t.client else 'Não informado',
                    'produto': produto_nome,
                    'valor': float(t.total),
                    'data': _format_dt_local_br(t.date),  # Vendas em UTC, converter para local
                    'tipo': 'venda'
                })
        
        return jsonify({
            'total_transacoes': total_transacoes,
            'saldo_atual': float(saldo_atual),
            'total_vendas': float(total_vendas),
            'total_sangrias': abs(float(total_sangrias)),  # Valor positivo para exibição
            'total_clientes': total_clientes,
            'total_produtos': total_produtos,
            'transacoes_recentes': recentes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/transaction', methods=['POST'])
def api_salvar_transaction():
    """API para salvar nova transação com múltiplos pagamentos"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not data.get('items') or not data.get('total'):
            return jsonify({'error': 'Campos obrigatórios faltando'}), 400
        
        # Validar pagamentos
        payments = data.get('payments', [])
        if not payments:
            return jsonify({'error': 'É necessário informar pelo menos um pagamento'}), 400
        
        # Verificar se o total dos pagamentos corresponde ao total da transação
        total_payments = sum(p['amount'] for p in payments)
        if abs(total_payments - float(data['total'])) > 0.01:  # Tolerância de 1 centavo
            return jsonify({'error': 'Total dos pagamentos não corresponde ao total da transação'}), 400
        
        # Criar nova transação
        transaction = Transaction(
            client_id=data.get('client_id') if data.get('client_id') else None,
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
        
        # Adicionar pagamentos
        for payment_data in payments:
            # Validar método de pagamento
            payment_method = PaymentMethod.query.get(payment_data['payment_method_id'])
            if not payment_method:
                return jsonify({'error': f'Método de pagamento inválido: {payment_data["payment_method_id"]}'}), 400
            
            payment = Payment(
                transaction_id=transaction.id,
                payment_method_id=payment_data['payment_method_id'],
                amount=float(payment_data['amount'])
            )
            db.session.add(payment)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'transaction_id': transaction.id,
            'message': 'Transação registrada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/produtos-unicos')
def api_produtos_unicos():
    """API para lista de produtos únicos de todas as transações (incluindo deletados)"""
    try:
        # Buscar produtos únicos das transações
        produtos_query = db.session.query(
            Product.id,
            Product.name,
            Product.price,
            db.func.count(TransactionItem.id).label('usage_count')
        ).join(TransactionItem, Product.id == TransactionItem.product_id, isouter=True)\
         .group_by(Product.id, Product.name, Product.price)\
         .order_by(Product.name)
        
        produtos = produtos_query.all()
        
        # Adicionar produtos de transações sem ID (descrições personalizadas)
        descricoes_unicas = db.session.query(
            TransactionItem.description
        ).filter(
            TransactionItem.product_id.is_(None),
            TransactionItem.description.isnot(None),
            TransactionItem.description != ''
        ).distinct().order_by(TransactionItem.description).all()
        
        resultado = []
        
        # Produtos cadastrados
        for produto in produtos:
            resultado.append({
                'id': produto.id,
                'name': produto.name,
                'price': float(produto.price),
                'usage_count': produto.usage_count,
                'type': 'cadastrado'
            })
        
        # Produtos personalizados (sem cadastro)
        for desc in descricoes_unicas:
            resultado.append({
                'id': None,
                'name': desc.description,
                'price': None,
                'usage_count': 1,
                'type': 'personalizado'
            })
        
        # Ordenar por nome
        resultado.sort(key=lambda x: x['name'].lower())
        
        return jsonify(resultado)
        
    except Exception as e:
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

@main_bp.route('/api/produtos/<int:produto_id>/preco', methods=['PUT'])
def api_atualizar_preco(produto_id):
    """API para atualizar preço de produto (afeta apenas futuras vendas)"""
    try:
        produto = Product.query.get_or_404(produto_id)
        data = request.get_json()
        
        if not data.get('preco') or float(data['preco']) < 0:
            return jsonify({'error': 'Preço inválido'}), 400
        
        # Atualizar preço do produto
        produto.price = float(data['preco'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preço atualizado com sucesso',
            'novo_preco': float(produto.price)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/retirada', methods=['POST'])
def api_retirada():
    """API para registrar retirada de caixa com tipo específico"""
    try:
        data = request.get_json()
        valor = data.get('valor')
        motivo = data.get('motivo')
        payment_method_id = data.get('payment_method_id')
        
        if not valor or not motivo:
            return jsonify({'error': 'Valor e motivo são obrigatórios'}), 400

        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return jsonify({'error': 'Valor inválido'}), 400

        if valor <= 0:
            return jsonify({'error': 'Valor deve ser maior que zero'}), 400
        
        if not payment_method_id:
            return jsonify({'error': 'Tipo de pagamento é obrigatório'}), 400
        
        # Validar método de pagamento
        payment_method = PaymentMethod.query.get(payment_method_id)
        if not payment_method:
            return jsonify({'error': 'Método de pagamento inválido'}), 400
        
        # Verificar saldo disponível para o método específico (considera sangrias anteriores)
        from sqlalchemy import func
        saldo_metodo = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_method_id == payment_method_id
        ).scalar() or 0

        # Normalizar para float (evita comparação float vs Decimal)
        saldo_metodo = float(saldo_metodo)
        
        if valor > saldo_metodo:
            return jsonify({
                'error': f'Saldo insuficiente no método {payment_method.name}! Saldo disponível: R$ {float(saldo_metodo):.2f}',
                'saldo_disponivel': float(saldo_metodo),
                'metodo_nome': payment_method.name
            }), 400
        
        # Calcular novo saldo
        novo_saldo = saldo_metodo - valor
        
        # Criar transação de sangria (valor negativo)
        sangria = Transaction(
            total=-valor,  # Valor negativo para sangria
            notes=f"SANGRIA: {motivo} [{payment_method.name}]",
            date=datetime.utcnow()
        )
        
        db.session.add(sangria)
        db.session.flush()  # Obter ID da transação
        
        # Criar pagamento negativo para o método específico
        payment_sangria = Payment(
            transaction_id=sangria.id,
            payment_method_id=payment_method_id,
            amount=-valor  # Valor negativo para sangria
        )
        
        db.session.add(payment_sangria)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Sangria registrada com sucesso no caixa {payment_method.name}',
            'sangria_id': sangria.id,
            'saldo_anterior': float(saldo_metodo),
            'saldo_novo': float(novo_saldo),
            'valor_retirado': float(valor),
            'metodo_nome': payment_method.name,
            'metodo_cor': payment_method.color
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/saldo-caixa')
def api_saldo_caixa():
    """API para obter saldo atual do caixa (apenas vendas, sem descontar sangrias)"""
    try:
        # Calcular saldo total das vendas (apenas transações positivas)
        from sqlalchemy import func
        
        saldo = db.session.query(func.sum(Transaction.total)).filter(Transaction.total > 0).scalar() or 0
        
        return jsonify({
            'saldo': float(saldo)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/relatorios', methods=['GET', 'POST'])
def api_relatorios():
    """API para gerar relatórios"""
    try:
        # Forçar refresh dos dados para evitar cache
        db.session.expire_all()
        
        # Obter parâmetros - suporta GET (query string) e POST (JSON)
        if request.method == 'POST':
            data = request.get_json() or {}
            data_inicio = data.get('data_inicio')
            data_fim = data.get('data_fim')
            cliente = data.get('cliente')
            produtos_ids = data.get('produtos', [])  # Array de IDs
        else:
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            cliente = request.args.get('cliente')
            produtos_ids = request.args.getlist('produto')  # GET: múltiplos valores
        
        # Construir query - MODIFICADO para incluir todas as transações
        query = Transaction.query.outerjoin(TransactionItem).outerjoin(Product).outerjoin(Client)
        
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Transaction.date >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            # Adicionar 1 dia para incluir até o final do dia_fim
            from datetime import timedelta
            data_fim_dt = data_fim_dt + timedelta(days=1)
            query = query.filter(Transaction.date < data_fim_dt)
        
        if cliente:
            query = query.filter(Client.name.contains(cliente))
        
        # Filtrar por múltiplos produtos
        if produtos_ids:
            # Separar produtos cadastrados de personalizados
            produtos_cadastrados = []
            produtos_personalizados = []
            
            for pid in produtos_ids:
                # Converter para string para verificar prefixo
                pid_str = str(pid)
                if pid_str.startswith('custom_'):
                    # Produto personalizado (descrição)
                    nome_produto = pid_str.replace('custom_', '')
                    produtos_personalizados.append(nome_produto)
                else:
                    # Produto cadastrado (ID)
                    try:
                        produtos_cadastrados.append(int(pid))
                    except (ValueError, TypeError):
                        pass
            
            # Construir condições OR para produtos
            from sqlalchemy import or_
            condicoes_produto = []
            
            # Condição para produtos cadastrados por ID
            if produtos_cadastrados:
                condicoes_produto.append(Product.id.in_(produtos_cadastrados))
            
            # Condição para produtos personalizados por descrição
            if produtos_personalizados:
                condicoes_produto.append(TransactionItem.description.in_(produtos_personalizados))
            
            # Incluir sangrias/retiradas mesmo com filtro de produtos,
            # pois sangrias não possuem TransactionItem/Product e seriam filtradas.
            condicao_sangria = or_(
                Transaction.total < 0,
                Transaction.notes.like('SANGRIA:%'),
                Transaction.notes.like('RETIRADA:%')
            )

            # Aplicar filtro com OR (qualquer condição de produto OU sangria)
            if condicoes_produto:
                query = query.filter(or_(condicao_sangria, or_(*condicoes_produto)))
            else:
                query = query.filter(condicao_sangria)
        
        # Ordenação estável: por data (mais recente primeiro) e, em caso de empate,
        # por id (mais recente primeiro). Isso garante que sangrias apareçam na
        # ordem em que foram executadas.
        transactions = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
        
        # Formatar dados - MODIFICADO para lidar com sangrias e todas as transações
        dados = []
        for t in transactions:
            # Verificar se é uma sangria
            if t.notes and t.notes.startswith('SANGRIA:'):
                dados.append({
                    'id': t.id,
                    'cliente': 'SANGRIA',
                    'produto': 'Retirada de Caixa',
                    'valor': float(t.total),  # Valor negativo
                    'data': _format_dt_br(t.date),  # Sangrias já em horário local
                    'observacoes': t.notes.replace('SANGRIA: ', ''),
                    'tipo': 'sangria'
                })
            elif t.notes and t.notes.startswith('RETIRADA:'):
                # Para compatibilidade com dados antigos
                dados.append({
                    'id': t.id,
                    'cliente': 'SANGRIA',
                    'produto': 'Retirada de Caixa',
                    'valor': float(t.total),  # Valor negativo
                    'data': _format_dt_br(t.date),  # Sangrias já em horário local
                    'observacoes': t.notes.replace('RETIRADA: ', ''),
                    'tipo': 'sangria'
                })
            else:
                # Transações normais de vendas
                produto_nome = 'N/A'
                if t.items and len(t.items) > 0:
                    if t.items[0].product:
                        produto_nome = t.items[0].product.name
                    elif t.items[0].description:
                        produto_nome = t.items[0].description
                
                dados.append({
                    'id': t.id,
                    'cliente': t.client.name if t.client else 'Não informado',
                    'produto': produto_nome,
                    'valor': float(t.total),
                    'data': _format_dt_local_br(t.date),  # Vendas em UTC, converter para local
                    'observacoes': t.notes or '',
                    'tipo': 'venda'
                })
        
        response = make_response(jsonify({'dados': dados}))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
