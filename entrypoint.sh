#!/bin/sh
set -e

echo "Python executable: $(which python)"
python -m pip list

python manage.py migrate --noinput

python manage.py collectstatic --noinput --clear

python manage.py create_test_users || true

python manage.py assign_daily_tasks || true

exec gunicorn sea_sight.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --log-level info