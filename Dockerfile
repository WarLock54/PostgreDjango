FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt repo root'unda
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# myproject klasörü repo root'unda, /app/myproject olarak kopyala
COPY myproject/ ./myproject/

WORKDIR /app/myproject

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
