FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sea_sight/ ./sea_sight/
COPY beaches/ ./beaches/
COPY templates/ ./templates/
COPY static/ ./static/
COPY manage.py .

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "sea_sight.wsgi:application", "--bind", "0.0.0.0:8000"]