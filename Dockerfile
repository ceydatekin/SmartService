FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# src klasörünü kopyala
COPY src /app/src

# requirements.txt'yi kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# gRPC portunu aç
EXPOSE 50051

# Çalışma dizinini src olarak ayarla ve uygulamayı başlat
WORKDIR /app/src
CMD ["python", "main.py"]