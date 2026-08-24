#!/bin/bash
set -e
exec celery -A app.celery_app.celery_app worker --loglevel=info --concurrency=2
