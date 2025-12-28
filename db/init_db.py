"""Utility script to initialize the application database.

This script creates the database file (in the configured path) and creates tables.
"""
from app import create_app
from app.db import init_db


def main():
    app = create_app()
    init_db(app)
    print("Database initialized")


if __name__ == "__main__":
    main()
