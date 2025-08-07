# Adım 1: Temel imaj olarak Python 3.12'nin slim versiyonunu kullan
FROM python:3.12-slim

# apt'nin kurulum sırasında interaktif diyaloglar sormasını engelle
ENV DEBIAN_FRONTEND=noninteractive

# Adım 2: Gerekli sistem paketlerini, bağımlılıkları ve Chrome'u kur
# Bu adımları tek bir RUN komutunda birleştirerek Docker katman sayısını optimize ediyoruz.
RUN apt-get update && apt-get install -y \
    # Chrome kurulumu için gerekli
    wget \
    gnupg \
    ca-certificates \
    # Selenium'un çalışması için temel bağımlılıklar
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    --no-install-recommends \
    # Google'ın GPG anahtarını ekle ve Chrome deposunu sisteme tanıt (daha modern ve güvenli yöntem)
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    # Paket listesini YENİDEN güncelle ve Chrome'u yükle
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    # Kurulum sonrası temizlik yaparak imaj boyutunu küçült
    && apt-get purge -y --auto-remove wget gnupg \
    && rm -rf /var/lib/apt/lists/*

# Adım 3: Güvenlik için 'root' olmayan bir kullanıcı oluştur ve çalışma dizinini ayarla
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
USER appuser

# Adım 4: Bağımlılıkları yükle (root olmayan kullanıcı olarak)
COPY --chown=appuser:appuser requirements.txt .
# --user flag'i paketleri kullanıcının home dizinine kurar, sistem genelini kirletmez
RUN pip install --no-cache-dir --user -r requirements.txt

# Adım 5: Proje dosyalarını kopyala
COPY --chown=appuser:appuser . .

# Python'un kullanıcı bazlı kurulan paketleri bulabilmesi için PATH'i güncelle
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Container başladığında sunucuyu çalıştıracak komut
CMD ["python", "-m", "server"]