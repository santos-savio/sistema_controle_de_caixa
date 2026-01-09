"""Database helper module.

This module exposes the SQLAlchemy `db` object and helper to initialize
SQLite database with recommended pragmas (WAL) to improve concurrency.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event


db = SQLAlchemy()


def init_sqlite_pragmas(engine):
    """Attach pragmas (like WAL) on SQLite connect."""

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            # Enable WAL journal mode
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
        except Exception:
            # If engine is not SQLite, ignore
            pass


def init_db(app):
    """Initialize DB and apply pragmas."""
    with app.app_context():
        # attach pragmas to the underlying engine
        init_sqlite_pragmas(db.engine)
        db.create_all()
