FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production DATABASE_PATH=/data/microblog.sqlite3

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY run.py start.sh ./
RUN mkdir -p /data && chmod +x /app/start.sh

EXPOSE 8000
CMD ["/app/start.sh"]
