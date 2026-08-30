#!/usr/bin/env bash
set -e

# Executa as migrações no banco antes de subir a API
alembic upgrade head

# Inicia o servidor uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}