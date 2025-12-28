import os
import tempfile

import pytest

from app import create_app
from app.db import db, init_db
from app.models import Client, Product, Transaction, TransactionItem


@pytest.fixture
def app_tmp_dir(tmp_path, monkeypatch):
    """Create a temp instance path so the sqlite file is local and isolated."""
    instance_path = tmp_path / "instance"
    instance_path.mkdir()
    # configure app to use a sqlite db in tmp instance
    monkeypatch.setenv("FLASK_ENV", "testing")
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{instance_path / 'test.db'}"
    app.config["TESTING"] = True

    # initialize DB
    init_db(app)
    yield app

    # cleanup
    db.session.remove()


def test_create_and_query_client(app_tmp_dir):
    app = app_tmp_dir
    with app.app_context():
        client = Client(name="Test Client")
        db.session.add(client)
        db.session.commit()

        assert Client.query.filter_by(name="Test Client").first() is not None


def test_transaction_with_item(app_tmp_dir):
    app = app_tmp_dir
    with app.app_context():
        product = Product(name="Service A", price=100)
        db.session.add(product)
        db.session.commit()

        tx = Transaction(total=100)
        db.session.add(tx)
        db.session.commit()

        item = TransactionItem(transaction_id=tx.id, product_id=product.id, qty=1, unit_price=100, subtotal=100)
        db.session.add(item)
        db.session.commit()

        tx_db = Transaction.query.get(tx.id)
        assert len(tx_db.items) == 1
