FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

RUN python manage.py migrate --noinput

RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

CMD python manage.py create_test_users && gunicorn sea_sight.wsgi:application --bind 0.0.0.0:8000