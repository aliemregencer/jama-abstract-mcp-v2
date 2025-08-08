# app.py (Nihai ve Hata Düzeltmeli Sürüm)

import json
import re
import os
import base64
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
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
    """Makale başlığı ve anahtar kelimelerine göre tematik bir ikon seçer."""
    search_text = (article_title.lower() + ' ' + ' '.join(article_keywords)).lower()
    for icon_file, keywords in ICON_MAP.items():
        for keyword in keywords:
            if keyword in search_text:
                return f"icons/{icon_file}"
    return "icons/default.png"

def parse_jama_article(url: str):
    """Verilen URL'yi undetected-chromedriver ile açar ve içeriğini ayrıştırır. (data, error) tuple'ı döndürür."""
    html_content = None
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        print("undetected-chromedriver başlatılıyor...")
        driver = uc.Chrome(options=options, use_subprocess=True)
        print("Sayfaya gidiliyor...")
        driver.get(url)
        time.sleep(5) 
        html_content = driver.page_source
    except Exception as e:
        error_message = f"undetected-chromedriver hatası: {str(e)}"
        print(error_message)
        return None, error_message
    finally:
        if driver:
            driver.quit()

    if not html_content or len(html_content) < 1000:
        return None, f"HTML içerik alınamadı veya çok kısa geldi (uzunluk: {len(html_content)}). Bot koruması olabilir."

    soup = BeautifulSoup(html_content, 'html.parser')
    article_data = {
        'url': url, 'title': None, 'authors': [], 'publication_date': None,
        'doi': None, 'key_points': {}, 'abstract': {}, 'keywords': [],
    }

    title_tag = soup.find('h1', class_='meta-article-title')
    if not title_tag:
        return None, "Sayfa yapısı ayrıştırılamadı (makale başlığı bulunamadı)."
    article_data['title'] = title_tag.get_text(strip=True)
    
    try:
        for script_tag in soup.find_all('script', {'type': 'application/ld+json'}):
            if script_tag.string:
                json_content = json.loads(script_tag.string)
                if json_content.get('@type') == 'MedicalScholarlyArticle':
                    article_data['publication_date'] = json_content.get('datePublished')
                    article_data['keywords'] = json_content.get('keyWords', '').split(', ')
                    break
    except (json.JSONDecodeError, AttributeError, TypeError):
        print("JSON-LD verisi ayrıştırılamadı, devam ediliyor.")

    authors_limited = soup.select('.meta-authors--limited .wi-fullname')
    authors_remaining = soup.select('.meta-authors--remaining .wi-fullname')
    all_authors = authors_limited + authors_remaining
    author_affiliations_map = {}
    affiliations_list = soup.select('.meta-author-affiliations li')
    for li in affiliations_list:
        sup_tag = li.find('sup')
        if sup_tag:
            sup_num = sup_tag.get_text(strip=True)
            affiliation_text_div = li.find('div', class_='meta-author-name')
            if affiliation_text_div:
                affiliation_text = affiliation_text_div.get_text(strip=True).replace(sup_num, '', 1).strip()
                author_affiliations_map[sup_num] = affiliation_text
    for author in all_authors:
        name_tag = author.find('a') if author.find('a') else author
        sup_tags = name_tag.find_all('sup')
        aff_keys = [sup.get_text(strip=True) for sup in sup_tags]
        for sup in name_tag.find_all('sup'): sup.decompose()
        name = name_tag.get_text(strip=True).replace(',', '')
        author_info = {'name': name, 'affiliations': [author_affiliations_map.get(key) for key in aff_keys if author_affiliations_map.get(key)]}
        article_data['authors'].append(author_info)

    doi_tag = soup.find('span', class_='meta-citation-doi')
    if doi_tag: article_data['doi'] = doi_tag.get_text(strip=True).replace('doi:', '')
    
    abstract_section = soup.find('div', id='AbstractSection')
    if abstract_section:
        for p_tag in abstract_section.find_all('p'):
            strong_tag = p_tag.find('strong')
            if strong_tag:
                key = strong_tag.get_text(strip=True).lower().replace(':', '')
                span_tag = p_tag.find('span')
                if span_tag:
                    article_data['abstract'][key] = span_tag.get_text(strip=True)

    return article_data, None

def create_presentation(data, icon_path):
    """Verilen verilerle bir PowerPoint sunumu oluşturur ve dosya adını döndürür."""
    try:
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)
        blank_slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_slide_layout)

        def add_textbox(text, left, top, width, height, font_size=12, is_bold=False, font_color=RGBColor(0, 0, 0), align=PP_ALIGN.LEFT):
            textbox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
            text_frame = textbox.text_frame
            text_frame.clear()
            text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            text_frame.word_wrap = True
            p = text_frame.paragraphs[0]
            p.text = text
            p.font.name = 'Arial'
            p.font.size = Pt(font_size)
            p.font.bold = is_bold
            p.font.color.rgb = font_color
            p.alignment = align
            return textbox

        def add_background_box(left, top, width, height, color=RGBColor(0xF2, 0xF2, 0xF2)):
            from pptx.enum.shapes import MSO_SHAPE
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
            shape.fill.solid()
            shape.fill.fore_color.rgb = color
            shape.line.fill.background()
            return shape

        # ... Slayt içeriğini oluşturma ...
        # (Bu bölümün tamamı önceki mesajdakiyle aynı, değişiklik yok)

        filename = "JAMA_Graphical_Abstract.pptx"
        prs.save(filename)
        return filename, None # Başarılı durumda (dosya_adı, None) döndür
    except Exception as e:
        error_message = f"PowerPoint oluşturulurken hata oluştu: {str(e)}"
        print(error_message)
        return None, error_message # Hata durumunda (None, hata_mesajı) döndür

def create_graphical_abstract_from_url(url: str) -> str:
    """Ana fonksiyon: Tüm adımları yönetir ve sonucu JSON olarak döndürür."""
    print(f"İşlem başladı: {url}")
    parsed_data, parse_error = parse_jama_article(url)
    if parse_error:
        return json.dumps({"error": f"Makale verileri çekilemedi. Teknik Detay: {parse_error}"})

    thematic_icon_path = select_thematic_icon(
        parsed_data.get('title', ''), parsed_data.get('keywords', [])
    )
    
    local_filename, presentation_error = create_presentation(parsed_data, thematic_icon_path)
    if presentation_error:
        return json.dumps({"error": f"Sunum dosyası oluşturulamadı. Teknik Detay: {presentation_error}"})

    try:
        with open(local_filename, "rb") as pptx_file:
            encoded_string = base64.b64encode(pptx_file.read()).decode('utf-8')
        
        if os.path.exists(local_filename):
            os.remove(local_filename)
            
        result = {
            "message": "Sunum başarıyla oluşturuldu.",
            "filename": local_filename,
            "file_data_base64": encoded_string
        }
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Dosya Base64'e çevrilirken hata oluştu: {str(e)}"})

