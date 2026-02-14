FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libtiff6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use environment variable PORT or default to 8080
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} app:app