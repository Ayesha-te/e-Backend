#!/usr/bin/env bash
# Start script for Render/Unix-like environments
# - Ensures we are in the backend folder
# - Applies migrations
# - Starts Gunicorn
set -e
cd "$(dirname "$0")"
python manage.py migrate --noinput
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}