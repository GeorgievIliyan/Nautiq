#!/bin/sh
set -e

echo "====== Starting Entrypoint ======"
echo "Python executable: $(which python)"
python -m pip list

echo "====== Running migrations ======"
python manage.py migrate --noinput

echo "====== Collecting static files ======"
python manage.py collectstatic --noinput --clear

echo "====== Creating test users ======"
python manage.py create_test_users || echo "create_test_users failed (ignored)"

echo "====== Generating initial daily tasks ======"
python manage.py shell -c "from beaches.utils import generate_daily_tasks; generate_daily_tasks()" || echo "daily task generation failed (ignored)"

echo "====== Starting Gunicorn and Celery in background ======"
gunicorn sea_sight.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --log-level info &

celery -A sea_sight worker --loglevel=INFO &

celery -A sea_sight beat --loglevel=INFO