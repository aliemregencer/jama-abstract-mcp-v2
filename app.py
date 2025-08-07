import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE

# --- Global Değişkenler ve Haritalar ---
ICON_MAP = {
    "cardiology.png": ["heart", "cardiac", "cardiology", "myocardial", "arrhythmia", "heart failure"],
    "neurology.png": ["brain", "neuro", "neurology", "stroke", "alzheimer", "parkinson", "epilepsy"],
    "oncology.png": ["cancer", "oncology", "tumor", "chemotherapy", "carcinoma"],
    "public_health.png": ["population", "public health", "mortality", "epidemiology", "opioid", "addiction"],
    "genetics.png": ["gene", "genetic", "dna", "genome", "genomics"],
}

# --- Yardımcı Fonksiyonlar ---
def select_thematic_icon(article_title, article_keywords):
    search_text = (article_title.lower() + ' ' + ' '.join(article_keywords)).lower()
    for icon_file, keywords in ICON_MAP.items():
        for keyword in keywords:
            if keyword in search_text:
                return f"icons/{icon_file}"
    return "icons/default.png"

# ... (parse_jama_article ve create_presentation fonksiyonları buraya gelecek) ...
# Not: Bu fonksiyonları bir önceki adımdaki halleriyle buraya kopyalıyoruz.
def parse_jama_article(url):
    # Önceki adımdaki fonksiyonun aynısı
    html_content = None
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") # Docker içinde çalışırken önemli
    chrome_options.add_argument("--disable-dev-shm-usage") # Docker içinde çalışırken önemli
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        html_content = driver.page_source
    except Exception as e:
        print(f"Selenium ile sayfa yüklenirken bir hata oluştu: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()
    if not html_content: return None
    soup = BeautifulSoup(html_content, 'html.parser')
    # ... (geri kalan tüm parsing mantığı burada olacak, bir önceki cevaptan kopyalanabilir) ...
    # Bu kısmı kısa tutmak için özetliyorum, önceki kodun tamamını yapıştırmalısın.
    article_data = {
        'title': soup.find('h1', class_='meta-article-title').get_text(strip=True) if soup.find('h1', class_='meta-article-title') else "N/A",
        # ... diğer tüm veri çekme işlemleri ...
    }
    # Bu fonksiyonun tam halini önceki mesajdan kopyalayıp buraya yapıştır.
    return article_data


def create_presentation(data, icon_path):
    # Önceki adımdaki fonksiyonun aynısı
    prs = Presentation()
    # ... (geri kalan tüm pptx oluşturma mantığı burada olacak) ...
    filename = "JAMA_Graphical_Abstract.pptx"
    prs.save(filename)
    return filename

# --- ANA MCP ARACI FONKSİYONU ---
def create_graphical_abstract_from_url(url: str) -> str:
    """
    Verilen JAMA makale URL'sinden verileri çeker, ayrıştırır ve
    bir PowerPoint sunumu oluşturur. Oluşturulan dosyanın adını döndürür.
    """
    print(f"Makale ayrıştırılıyor: {url}")
    parsed_data = parse_jama_article(url)
    
    if not parsed_data:
        return "Makale verileri çekilemedi."

    print("İçeriğe göre tematik ikon seçiliyor...")
    thematic_icon_path = select_thematic_icon(
        parsed_data.get('title', ''),
        parsed_data.get('keywords', [])
    )
    
    print("PowerPoint sunumu oluşturuluyor...")
    output_filename = create_presentation(parsed_data, thematic_icon_path)
    
    return f"Sunum başarıyla oluşturuldu: {output_filename}"