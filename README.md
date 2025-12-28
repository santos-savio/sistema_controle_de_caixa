# Sistema de Controle de Caixa (MVP)

This repository contains a small local cash management application built with Python + Flask.

Quick start (development):

- Create a virtual environment and install packages:
  - PowerShell: `.\scripts\setup_env.ps1`

- Initialize database:
  - `python db/init_db.py`

- Run tests:
  - `pytest -q`

Project structure highlights:
- `app/` — flask app and models
- `db/init_db.py` — script to create database and tables
- `tests/` — pytest tests

All comments and identifiers are in English for consistency.
