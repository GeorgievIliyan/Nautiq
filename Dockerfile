FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py .
COPY sea_sight/ ./sea_sight/
COPY beaches/ ./beaches/
COPY beaches/templates/ ./templates/   # <--- правилният път
COPY static/ ./static/

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "sea_sight.wsgi:application", "--bind", "0.0.0.0:8000"]