from flask import Flask
from .db import db


def create_app(config_object: str = "config.Config") -> Flask:
    """Application factory creating the Flask app and initializing extensions.

    Args:
        config_object: import string for configuration (optional)
    Returns:
        Flask app instance
    """
    app = Flask(__name__, instance_relative_config=False, template_folder='../templates')
    app.config.from_object(config_object)

    # initialize extensions
    db.init_app(app)

    # register blueprints
    from .routes import main_bp
    from .config_routes import config_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(config_bp)

    # Ensure database and minimal data exist on first start
    with app.app_context():
        from .db import init_db
        init_db(app)
        _ensure_minimal_data()

    return app


def _ensure_minimal_data():
    """Create minimal seed data if tables are empty (idempotent)."""
    from .models import Product, PaymentMethod, SystemConfig

    # Produtos padrão (se não existirem)
    if not Product.query.first():
        default_products = [
            Product(name='Consulta', price=50.00),
            Product(name='Serviço Básico', price=100.00),
            Product(name='Serviço Premium', price=200.00),
        ]
        for p in default_products:
            db.session.add(p)
        db.session.commit()

    # Métodos de pagamento padrão (se não existirem)
    if not PaymentMethod.query.first():
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
        for method_data in default_methods:
            method = PaymentMethod(**method_data)
            db.session.add(method)
        db.session.commit()

    # PIN padrão (se não existir)
    if not SystemConfig.get_value('admin_pin'):
        SystemConfig.set_value('admin_pin', '1234', 'PIN de acesso ao painel administrativo')
