#!/usr/bin/env bash
# Start script for Render/Unix-like environments
# - Ensures we are in the backend folder
# - Applies migrations
# - Starts Gunicorn
set -e
cd "$(dirname "$0")"

# Optionally skip migrations if handled by Render's postdeployCommand
if [ -z "$SKIP_MIGRATE" ]; then
  python manage.py migrate --noinput
fi

exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}