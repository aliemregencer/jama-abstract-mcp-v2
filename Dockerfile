# Kararlı bir Python sürümü ile başlıyoruz
FROM python:3.12-slim

# Selenium'un çalışması için Chrome ve gerekli bağımlılıkları kuruyoruz
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    google-chrome-stable \
    --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list

# Proje dosyaları için bir çalışma dizini oluştur
WORKDIR /app

# Proje dosyalarını container'a kopyala
COPY . .

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir -r requirements.txt

# Container başladığında sunucuyu çalıştıracak komut
CMD ["python", "-m", "server"]