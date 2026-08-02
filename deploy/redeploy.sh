#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/home/django_user/apps/uae_crtn"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"

cd "$PROJECT_DIR"

echo "Running migrations..."
"$PYTHON_BIN" manage.py migrate

echo "Collecting static files..."
"$PYTHON_BIN" manage.py collectstatic --noinput

echo "Restarting Gunicorn..."
sudo systemctl restart curtain_master_gunicorn.service

echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "Done."
