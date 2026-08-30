#!/usr/bin/env bash
set -e

# Inicia o worker do Celery
exec celery -A app.celery_app.celery_app worker --loglevel=info
