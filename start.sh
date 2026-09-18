#!/bin/sh
set -eu

if [ -n "${DEMO_PASSWORD:-}" ]; then
  flask --app run.py seed-demo
fi

exec gunicorn --bind "0.0.0.0:${PORT:-8000}" --workers 1 run:app
