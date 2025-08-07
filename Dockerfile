# Kararlı bir Python sürümü ile başlıyoruz
FROM python:3.12-slim

# Adım 1: Paket listesini güncelle ve Chrome kurulumu için gerekli araçları yükle
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    --no-install-recommends

# Adım 2: Google'ın GPG anahtarını ekle (daha modern ve güvenli yöntemle)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg

# Adım 3: Google Chrome deposunu sisteme tanıt
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Adım 4: Paket listesini YENİDEN güncelle ve Chrome'u yükle
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends \
    # Kurulum sonrası temizlik yaparak imaj boyutunu küçült
    && rm -rf /var/lib/apt/lists/*

# Proje dosyaları için bir çalışma dizini oluştur
WORKDIR /app

# Proje dosyalarını container'a kopyala
COPY . .

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir -r requirements.txt

# Container başladığında sunucuyu çalıştıracak komut
CMD ["python", "-m", "server"]