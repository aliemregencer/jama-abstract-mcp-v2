# app.py dosyasının tamamını bu güncel versiyonla değiştir

import json
import re
import os
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE

# --- İKON EŞLEŞTİRME HARİTASI (Değişiklik yok) ---
ICON_MAP = {
    "cardiology.png": ["heart", "cardiac", "cardiology", "myocardial", "arrhythmia", "heart failure"],
    "neurology.png": ["brain", "neuro", "neurology", "stroke", "alzheimer", "parkinson", "epilepsy"],
    "oncology.png": ["cancer", "oncology", "tumor", "chemotherapy", "carcinoma"],
    "public_health.png": ["population", "public health", "mortality", "epidemiology", "opioid", "addiction"],
    "genetics.png": ["gene", "genetic", "dna", "genome", "genomics"],
}

def select_thematic_icon(article_title, article_keywords):
    # Bu fonksiyonda değişiklik yok
    search_text = (article_title.lower() + ' ' + ' '.join(article_keywords)).lower()
    for icon_file, keywords in ICON_MAP.items():
        for keyword in keywords:
            if keyword in search_text:
                return f"icons/{icon_file}"
    return "icons/default.png"

def parse_jama_article(url):
    # GÜNCELLEME: Bu fonksiyon artık (data, error) formatında bir tuple döndürecek
    html_content = None
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        html_content = driver.page_source
    except Exception as e:
        # GÜNCELLEME: Hatayı print edip None dönmek yerine, hatayı string olarak döndür
        error_message = f"Selenium ile sayfa yüklenirken bir hata oluştu: {str(e)}"
        print(error_message)
        return None, error_message # Hata durumunda (None, "hata mesajı") döndür
    finally:
        if 'driver' in locals():
            driver.quit()

    if not html_content:
        error_message = "HTML içerik alınamadı (sayfa boş geldi)."
        print(error_message)
        return None, error_message

    # ... (Geri kalan parsing kodu aynı, sadece en sonda return değerini güncelleyeceğiz)
    soup = BeautifulSoup(html_content, 'html.parser')
    article_data = {
        'url': url, 'title': None, 'authors': [], 'publication_date': None,
        'doi': None, 'key_points': {}, 'abstract': {}, 'keywords': [],
        'full_text': {}, 'references': []
    }
    # ... (Tüm parsing kodları buraya gelecek, değişiklik yok)
    # Örnek olarak bir tanesini ekliyorum, geri kalanını önceki koddan almalısın
    title_tag = soup.find('h1', class_='meta-article-title')
    if title_tag:
        article_data['title'] = title_tag.get_text(strip=True)
    else:
        # GÜNCELLEME: Parsing başarısız olursa da hata döndür
        error_message = "Makale başlığı (title) bulunamadı. Sayfa yapısı değişmiş olabilir."
        print(error_message)
        return None, error_message
    
    # ... (Diğer tüm parsing adımları) ...
    
    return article_data, None # Başarılı durumda (data, None) döndür

# ... create_presentation fonksiyonunda değişiklik yok ...
def create_presentation(data, icon_path):
    # Önceki adımdaki fonksiyonun aynısı
    # ...
    filename = "JAMA_Graphical_Abstract.pptx"
    prs.save(filename)
    return filename

def create_graphical_abstract_from_url(url: str) -> str:
    # GÜNCELLEME: Hata mesajını işlemek için güncellendi
    print(f"Makale ayrıştırılıyor: {url}")
    parsed_data, error = parse_jama_article(url) # Artık iki değer alıyoruz
    
    if error:
        # Eğer parse_jama_article bir hata döndürdüyse, o hatayı direkt olarak kullanıcıya göster.
        return f"HATA: Makale verileri çekilemedi. Teknik Detay: {error}"

    print("İçeriğe göre tematik ikon seçiliyor...")
    thematic_icon_path = select_thematic_icon(
        parsed_data.get('title', ''),
        parsed_data.get('keywords', [])
    )
    
    print("PowerPoint sunumu oluşturuluyor...")
    local_filename = create_presentation(parsed_data, thematic_icon_path)
    
    # ... (file.io yükleme kısmı aynı kalacak) ...
    # ...

    return f"Sunum başarıyla oluşturuldu: {local_filename}" # Örnek