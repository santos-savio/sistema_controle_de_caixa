from flask import Blueprint, render_template, request, jsonify, make_response
from app.models import db, Client, Product, Transaction, TransactionItem, SystemConfig, PaymentMethod, Payment
from datetime import datetime

# Criar um blueprint adicional para APIs de configuração
config_bp = Blueprint('config', __name__)

@config_bp.route('/api/pin', methods=['GET'])
def api_get_pin():
    """API para obter o PIN atual"""
    try:
        pin = SystemConfig.get_value('admin_pin', '1234')  # PIN padrão
        return jsonify({'pin': pin})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/pin', methods=['POST'])
def api_set_pin():
    """API para definir o PIN"""
    try:
        data = request.get_json()
        new_pin = data.get('pin')
        
        if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
            return jsonify({'error': 'PIN deve ter exatamente 4 dígitos numéricos'}), 400
        
        # Salvar PIN no banco
        SystemConfig.set_value('admin_pin', new_pin, 'PIN de acesso ao painel administrativo')
        
        return jsonify({'success': True, 'message': 'PIN atualizado com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/pin/verify', methods=['POST'])
def api_verify_pin():
    """API para verificar o PIN"""
    try:
        data = request.get_json()
        pin_informado = data.get('pin')
        
        if not pin_informado:
            return jsonify({'error': 'PIN é obrigatório'}), 400
        
        pin_salvo = SystemConfig.get_value('admin_pin', '1234')
        
        if pin_informado == pin_salvo:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'PIN incorreto'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/payment-methods', methods=['GET'])
def api_payment_methods():
    """API para obter métodos de pagamento ativos"""
    try:
        methods = PaymentMethod.get_active_methods()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'code': m.code,
            'description': m.description,
            'color': m.color
        } for m in methods])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/payment-methods', methods=['POST'])
def api_create_payment_method():
    """API para criar novo método de pagamento"""
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('name') or not data.get('code'):
            return jsonify({'error': 'Nome e código são obrigatórios'}), 400
        
        # Verificar se já existe
        existing = PaymentMethod.query.filter(
            (PaymentMethod.name == data['name']) | 
            (PaymentMethod.code == data['code'])
        ).first()
        
        if existing:
            return jsonify({'error': 'Método de pagamento já existe'}), 400
        
        # Criar novo método
        method = PaymentMethod(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            color=data.get('color', '#007bff')
        )
        
        db.session.add(method)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Método de pagamento criado com sucesso',
            'method': {
                'id': method.id,
                'name': method.name,
                'code': method.code,
                'description': method.description,
                'color': method.color
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/balances', methods=['GET'])
def api_balances():
    """API para consultar saldos por tipo de pagamento"""
    try:
        # Obter saldos por método de pagamento
        balances = Payment.get_balance_by_method()
        
        # Calcular sangrias por método
        sangrias = db.session.query(
            PaymentMethod.name,
            PaymentMethod.code,
            PaymentMethod.color,
            db.func.sum(Payment.amount).label('total')
        ).join(Payment).filter(Payment.amount < 0).group_by(
            PaymentMethod.id, PaymentMethod.name, PaymentMethod.code, PaymentMethod.color
        ).all()
        
        # Criar dicionário de sangrias
        sangria_dict = {s.code: float(s.total) for s in sangrias}
        
        # Formatar resposta
        result = []
        for balance in balances:
            code = balance.code
            total_sales = float(balance.total) if balance.total else 0
            total_sangrias = abs(sangria_dict.get(code, 0))
            # Saldo disponível no método (vendas - sangrias)
            net_balance = total_sales - total_sangrias
            
            result.append({
                'name': balance.name,
                'code': code,
                'color': balance.color,
                'total_sales': total_sales,
                'total_sangrias': total_sangrias,
                'balance': net_balance
            })
        
        return jsonify({'balances': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
