"""SQLAlchemy models for the cash management app.

Simple models are defined for the MVP: Client, Product, Transaction, TransactionItem.
"""
from datetime import datetime
from decimal import Decimal
from .db import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Client {self.id} {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(50), default="service")
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Product {self.id} {self.name} {self.price}>"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)

    client = db.relationship("Client", backref=db.backref("transactions", lazy=True))
    items = db.relationship("TransactionItem", backref="transaction", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Transaction {self.id} {self.total}>"


class TransactionItem(db.Model):
    __tablename__ = "transaction_items"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    qty = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal('0.00'))

    product = db.relationship("Product")

    def __repr__(self):
        return f"<Item {self.id} tx={self.transaction_id} product={self.product_id}>"


class SystemConfig(db.Model):
    __tablename__ = "system_config"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Config {self.key}={self.value}>"

    @classmethod
    def get_value(cls, key, default=None):
        """Get configuration value by key"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default

    @classmethod
    def set_value(cls, key, value, description=None):
        """Set configuration value by key"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
            config.updated_at = datetime.utcnow()
        else:
            config = cls(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()
        return config