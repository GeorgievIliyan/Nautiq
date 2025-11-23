FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN mkdir -p /app/staticfiles

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]