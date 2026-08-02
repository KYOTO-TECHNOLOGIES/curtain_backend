#!/usr/bin/env bash

set -euo pipefail

echo "Restarting Gunicorn..."
sudo systemctl restart curtain_master_gunicorn.service

echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "Done."
