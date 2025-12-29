from flask import Blueprint, render_template, request, jsonify, make_response
from app.models import db, Client, Product, Transaction, TransactionItem, SystemConfig
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
