#!/bin/sh
set -e

python manage.py migrate --noinput

python manage.py collectstatic --noinput --clear

python manage.py create_test_users || true

exec gunicorn sea_sight.wsgi:application --bind 0.0.0.0:8000