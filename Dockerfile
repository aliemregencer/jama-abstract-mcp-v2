# Kararlı bir Python sürümü ile başlıyoruz
FROM python:3.12-slim

# Docker'da Selenium'un ihtiyaç duyacağı Chrome'u ve bağımlılıkları kuruyoruz
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    # Chrome'un ihtiyaç duyduğu kütüphaneler
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    --no-install-recommends

# Google Chrome'u yüklüyoruz
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    --no-install-recommends

# Proje dosyaları için bir çalışma dizini oluştur
WORKDIR /app

# Proje dosyalarını container'a kopyala
COPY . .

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir -r requirements.txt

# Container başladığında sunucuyu çalıştıracak komut
CMD ["python", "-m", "server"]