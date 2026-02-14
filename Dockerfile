FROM python:3.11-slim

# Install system dependencies for Pillow/Matplotlib
RUN apt-get update && apt-get install -y \
    libtiff6 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libfreetype6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app"]