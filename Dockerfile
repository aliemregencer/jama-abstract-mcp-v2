FROM python:3.11-slim

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome repository'sini ekle
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Chrome ve gerekli bağımlılıkları kur
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Chrome driver'ı otomatik kurulum için hazırla
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER_VERSION=120.0.6099.109

# Python bağımlılıklarını kur
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . /app

# Chrome için gerekli environment variable'ları ayarla
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=. \
    DISPLAY=:99 \
    CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu --disable-extensions --disable-plugins --disable-images --disable-javascript"

# Port'u aç
EXPOSE 8000

# Uygulamayı başlat
CMD ["python", "-m", "server"]
