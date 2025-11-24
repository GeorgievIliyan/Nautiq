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

echo "====== Assigning tasks ======"
python manage.py assign_tasks || echo "assign_tasks failed (ignored)"

echo "====== Starting Gunicorn ======"
exec gunicorn sea_sight.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --log-level info