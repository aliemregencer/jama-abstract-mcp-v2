# app.py dosyasının tamamını bu güncel versiyonla değiştir

import json
import re
import os
import base64
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
import requests
import time
from datetime import datetime

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
    
    # JSON-LD verilerini parse et
    try:
        for script_tag in soup.find_all("script", {"type": "application/ld+json"}):
            if script_tag.string:
                json_content = json.loads(script_tag.string)
                if json_content.get("@type") == "MedicalScholarlyArticle":
                    article_data["publication_date"] = json_content.get("datePublished")
                    article_data["keywords"] = json_content.get("keyWords", "").split(", ")
                    break
    except (json.JSONDecodeError, AttributeError, TypeError):
        print("JSON-LD verisi ayrıştırılırken bir sorun oluştu, devam ediliyor.")
    
    # Başlık
    title_tag = soup.find('h1', class_='meta-article-title')
    if title_tag:
        article_data['title'] = title_tag.get_text(strip=True)
    else:
        # GÜNCELLEME: Parsing başarısız olursa da hata döndür
        error_message = "Makale başlığı (title) bulunamadı. Sayfa yapısı değişmiş olabilir."
        print(error_message)
        return None, error_message
    
    # Yazarlar
    authors_limited = soup.select(".meta-authors--limited .wi-fullname")
    authors_remaining = soup.select(".meta-authors--remaining .wi-fullname")
    all_authors = authors_limited + authors_remaining
    author_affiliations_map = {}
    affiliations_list = soup.select(".meta-author-affiliations li")
    for li in affiliations_list:
        sup_tag = li.find("sup")
        if sup_tag:
            sup_num = sup_tag.get_text(strip=True)
            affiliation_text_div = li.find("div", class_="meta-author-name")
            if affiliation_text_div:
                affiliation_text = (
                    affiliation_text_div.get_text(strip=True)
                    .replace(sup_num, "", 1)
                    .strip()
                )
                author_affiliations_map[sup_num] = affiliation_text
    for author in all_authors:
        name_tag = author.find("a") if author.find("a") else author
        sup_tags = name_tag.find_all("sup")
        aff_keys = [sup.get_text(strip=True) for sup in sup_tags]
        for sup in name_tag.find_all("sup"):
            sup.decompose()
        name = name_tag.get_text(strip=True).replace(",", "")
        author_info = {
            "name": name,
            "affiliations": [
                author_affiliations_map.get(key)
                for key in aff_keys
                if author_affiliations_map.get(key)
            ],
        }
        article_data["authors"].append(author_info)
    
    # DOI
    doi_tag = soup.find("span", class_="meta-citation-doi")
    if doi_tag:
        article_data["doi"] = doi_tag.get_text(strip=True).replace("doi:", "")
    
    # Key Points
    key_points_section = soup.find("span", class_="heading-text", string="Key Points")
    if key_points_section:
        current_element = key_points_section.find_next_sibling("p")
        while current_element and current_element.name == "p":
            strong_tag = current_element.find("strong")
            if strong_tag:
                key = strong_tag.get_text(strip=True).lower()
                value = (
                    current_element.find("span").get_text(strip=True)
                    if current_element.find("span")
                    else ""
                )
                article_data["key_points"][key] = value
            current_element = current_element.find_next_sibling()
    
    # Abstract
    abstract_section = soup.find("div", id="AbstractSection")
    if abstract_section:
        for p_tag in abstract_section.find_all("p"):
            strong_tag = p_tag.find("strong")
            if strong_tag:
                key = strong_tag.get_text(strip=True).lower().replace(":", "")
                span_tag = p_tag.find("span")
                if span_tag:
                    article_data["abstract"][key] = span_tag.get_text(strip=True)
    
    # Full Text
    full_text_div = soup.find("div", class_="article-full-text")
    if full_text_div:
        first_header = full_text_div.find("div", class_="section-type-section")
        if first_header:
            current_section_title = "introduction"
            article_data["full_text"][current_section_title] = ""
            for element in first_header.find_all_previous("p", class_="para"):
                article_data["full_text"][current_section_title] = (
                    element.get_text(" ", strip=True)
                    + "\n"
                    + article_data["full_text"][current_section_title]
                )

            for element in first_header.find_next_siblings():
                if element.name == "div" and "section-type-section" in element.get(
                    "class", []
                ):
                    current_section_title = element.get_text(strip=True).lower()
                    article_data["full_text"][current_section_title] = ""
                elif element.name == "p" and "para" in element.get("class", []):
                    if current_section_title:
                        article_data["full_text"][current_section_title] += (
                            element.get_text(" ", strip=True) + "\n"
                        )
    
    # References
    references_div = soup.find("div", class_="references")
    if references_div:
        for ref in references_div.find_all("div", class_="reference"):
            ref_content = ref.find("div", class_="reference-content")
            if ref_content:
                article_data["references"].append(ref_content.get_text(" ", strip=True))
    
    return article_data, None # Başarılı durumda (data, None) döndür

def create_presentation(data, icon_path):
    """
    Verilen verilerle jama_va.pptx template'ini kullanarak bir PowerPoint sunumu oluşturur.
    Template'deki şekil isimlerine göre içerik yerleştirir.
    """
    # Template dosyasını aç
    template_path = "templates/jama_va.pptx"
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template dosyası bulunamadı: {template_path}")
    
    prs = Presentation(template_path)
    
    # Template'deki şekilleri bul ve içerikle doldur
    for slide in prs.slides:
        for shape in slide.shapes:
            shape_name = shape.name if hasattr(shape, 'name') else ""
            
            # Şekil ismine göre içerik yerleştir
            if shape_name == "title":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    p.text = data.get("title", "Başlık Bulunamadı")
                    p.font.bold = True
                    p.font.size = Pt(18)
                    p.font.color.rgb = RGBColor(0xED, 0x09, 0x73)
            
            elif shape_name == "population_subtitle":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    p.text = "POPULATION"
                    p.font.bold = True
                    p.font.size = Pt(11)
                    p.font.color.rgb = RGBColor(0xED, 0x09, 0x73)
            
            elif shape_name == "population_description":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    population_text = data["abstract"].get(
                        "design, setting, and participants", 
                        "Nüfus verisi bulunamadı."
                    )
                    p.text = population_text
                    p.font.size = Pt(10)
                    # Metin kutusuna sığdır
                    shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                    shape.text_frame.word_wrap = True
            
            elif shape_name == "intervention_subtitle":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    p.text = "INTERVENTION"
                    p.font.bold = True
                    p.font.size = Pt(11)
                    p.font.color.rgb = RGBColor(0xED, 0x09, 0x73)
            
            elif shape_name == "intervention_description":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    intervention_text = data["abstract"].get(
                        "interventions", 
                        "Müdahale verisi bulunamadı."
                    )
                    p.text = intervention_text
                    p.font.size = Pt(10)
                    shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                    shape.text_frame.word_wrap = True
            
            elif shape_name == "settings_locations_description":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    settings_text = data["abstract"].get(
                        "design, setting, and participants", 
                        "Ayarlar ve konumlar bulunamadı."
                    )
                    p.text = settings_text
                    p.font.size = Pt(10)
                    shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                    shape.text_frame.word_wrap = True
            
            elif shape_name == "primary_outcome_description":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    outcome_text = data["abstract"].get(
                        "main outcomes and measures", 
                        "Birincil sonuç bulunamadı."
                    )
                    p.text = outcome_text
                    p.font.size = Pt(10)
                    shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                    shape.text_frame.word_wrap = True
            
            elif shape_name == "findings_description_1":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    findings_text = data["abstract"].get(
                        "results", 
                        "Bulgular bulunamadı."
                    )
                    # Bulguları iki parçaya böl
                    if findings_text and len(findings_text) > 200:
                        words = findings_text.split()
                        mid_point = len(words) // 2
                        p.text = " ".join(words[:mid_point])
                    else:
                        p.text = findings_text
                    p.font.size = Pt(10)
                    shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                    shape.text_frame.word_wrap = True
            
            elif shape_name == "findings_description_2":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    findings_text = data["abstract"].get(
                        "results", 
                        "Bulgular bulunamadı."
                    )
                    # Bulguları iki parçaya böl
                    if findings_text and len(findings_text) > 200:
                        words = findings_text.split()
                        mid_point = len(words) // 2
                        p.text = " ".join(words[mid_point:])
                    else:
                        p.text = ""
                    p.font.size = Pt(10)
                    shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                    shape.text_frame.word_wrap = True
            
            elif shape_name == "footer_citation":
                if hasattr(shape, 'text_frame'):
                    shape.text_frame.clear()
                    p = shape.text_frame.paragraphs[0]
                    first_author = data["authors"][0]["name"] if data["authors"] else "Yazar Yok"
                    citation = f"{first_author.split(',')[0]} L, et al. {data.get('title', 'Başlık')}; a randomized clinical trial. JAMA Netw Open. {data.get('publication_date', 'Tarih Yok')} doi:{data.get('doi', 'DOI Yok')}"
                    p.text = citation
                    p.font.size = Pt(8)
                    p.font.color.rgb = RGBColor(128, 128, 128)
            
            # Metin kutularını da kontrol et
            elif "Metin kutusu" in shape_name:
                if hasattr(shape, 'text_frame'):
                    # Metin kutusunun konumuna göre içerik yerleştir
                    left = shape.left
                    top = shape.top
                    
                    # Sol taraftaki metin kutuları (popülasyon alanı)
                    if left < Inches(3):
                        if "16" in shape_name or "17" in shape_name:
                            shape.text_frame.clear()
                            p = shape.text_frame.paragraphs[0]
                            p.text = data["abstract"].get(
                                "design, setting, and participants", 
                                "Detay bilgi bulunamadı."
                            )
                            p.font.size = Pt(9)
                            shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                            shape.text_frame.word_wrap = True
                    
                    # Sağ taraftaki metin kutuları (bulgular alanı)
                    elif left > Inches(3):
                        if "20" in shape_name or "21" in shape_name or "22" in shape_name:
                            shape.text_frame.clear()
                            p = shape.text_frame.paragraphs[0]
                            p.text = data["abstract"].get(
                                "conclusions and relevance", 
                                "Sonuç bilgisi bulunamadı."
                            )
                            p.font.size = Pt(9)
                            shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                            shape.text_frame.word_wrap = True

    # Dosyayı kaydet
    filename = "JAMA_VA_Abstract.pptx"
    prs.save(filename)
    print(f"\nVA formatında sunum başarıyla oluşturuldu ve kaydedildi: {filename}")
    return filename

def upload_to_github_release(
    filename: str,
    title: str,
    repo_full_name: str,
    github_token: str,
) -> tuple[str | None, str | None]:
    """
    Verilen `repo_full_name` (örn. "kullaniciadi/repoadi") ve `github_token` ile GitHub'da
    `latest-abstract` etiketiyle bir Release oluşturur, varsa eskisini siler ve `filename`
    dosyasını bu release'e asset olarak yükler. Başarılıysa herkese açık indirme linkini döndürür.
    """
    try:
        if not repo_full_name or "/" not in repo_full_name:
            msg = "Geçersiz repo formatı. 'kullaniciadi/repoadi' şeklinde olmalı."
            print(msg)
            return None, msg
        if not github_token:
            msg = "GitHub token gerekli, işlem iptal edildi."
            print(msg)
            return None, msg

        repo_owner, repo_name = repo_full_name.split("/", 1)
        release_tag = "latest-abstract"
        safe_title = title or "JAMA Abstract"
        release_name = f"JAMA Abstract - {safe_title[:70]}"  # daha kısa

        # API headers
        headers_json = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }

        api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

        # Token ve repo erişimini doğrula
        repo_check = requests.get(api_base, headers=headers_json)
        if repo_check.status_code != 200:
            msg = (
                f"Repo erişimi başarısız: {repo_check.status_code} {repo_check.text}. "
                "Repo adını ve token izinlerini kontrol edin."
            )
            print(msg)
            return None, msg

        # Mevcut release'i kontrol et ve varsa sil
        print("Mevcut release kontrol ediliyor...")
        response = requests.get(f"{api_base}/releases/tags/{release_tag}", headers=headers_json)
        if response.status_code == 200:
            release = response.json()
            release_id = release["id"]
            # Asset'leri sil
            assets_resp = requests.get(f"{api_base}/releases/{release_id}/assets", headers=headers_json)
            if assets_resp.status_code == 200:
                for asset in assets_resp.json():
                    requests.delete(f"{api_base}/releases/assets/{asset['id']}", headers=headers_json)
            # Release'i sil
            requests.delete(f"{api_base}/releases/{release_id}", headers=headers_json)
            # Tag'i de sil (aksi halde aynı tag ile oluşturma başarısız olabilir)
            requests.delete(f"{api_base}/git/refs/tags/{release_tag}", headers=headers_json)
            print("Eski release ve etiketi silindi.")
        elif response.status_code not in (200, 404):
            msg = f"Release kontrolünde hata: {response.status_code} {response.text}"
            print(msg)
            return None, msg

        # Yeni release oluştur
        print("Yeni release oluşturuluyor...")
        release_data = {
            "tag_name": release_tag,
            "name": release_name,
            "body": (
                "JAMA Network Open makalesi için oluşturulan görsel özet.\n\n"
                f"Makale: {safe_title}\n"
                f"Oluşturulma tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            "draft": False,
            "prerelease": False,
        }
        response = requests.post(f"{api_base}/releases", json=release_data, headers=headers_json)
        if response.status_code != 201:
            # Özel durum: Repository is empty -> README oluşturarak başlatmayı dene, sonra tekrar dene
            if response.status_code == 422 and "Repository is empty" in response.text:
                print("Repo boş. README.md oluşturarak repo'yu başlatmayı deniyoruz...")
                repo_meta = requests.get(api_base, headers=headers_json)
                default_branch = "main"
                if repo_meta.status_code == 200:
                    default_branch = repo_meta.json().get("default_branch") or "main"

                readme_content = (
                    f"# {repo_name}\n\nBu repo otomatik olarak görsel özet dosyalarını (PPTX) barındırmak için başlatıldı."
                )
                create_resp = requests.put(
                    f"{api_base}/contents/README.md",
                    headers=headers_json,
                    json={
                        "message": "Initialize repository with README",
                        "content": base64.b64encode(readme_content.encode("utf-8")).decode("utf-8"),
                        "branch": default_branch,
                    },
                )
                if create_resp.status_code in (201, 200):
                    print("README.md oluşturuldu. Release tekrar oluşturuluyor...")
                    time.sleep(1)
                    response = requests.post(
                        f"{api_base}/releases", json=release_data, headers=headers_json
                    )
                else:
                    msg = (
                        "Repo boş ve README oluşturma başarısız: "
                        f"{create_resp.status_code} {create_resp.text}"
                    )
                    print(msg)
                    return None, msg

            if response.status_code != 201:
                msg = f"Release oluşturma hatası: {response.status_code} {response.text}"
                print(msg)
                return None, msg

        release_info = response.json()
        upload_url = release_info["upload_url"].split("{")[0]

        # Dosyayı yükle
        print("Dosya yükleniyor...")
        with open(filename, "rb") as f:
            binary = f.read()
        headers_upload = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/octet-stream",
        }
        upload_resp = requests.post(
            f"{upload_url}?name={os.path.basename(filename)}",
            data=binary,
            headers=headers_upload,
        )
        if upload_resp.status_code != 201:
            msg = f"Dosya yükleme hatası: {upload_resp.status_code} {upload_resp.text}"
            print(msg)
            return None, msg

        asset_info = upload_resp.json()
        download_url = asset_info.get("browser_download_url")
        if not download_url:
            msg = "browser_download_url bulunamadı."
            print(msg)
            return None, msg
        print(f"Dosya başarıyla yüklendi: {download_url}")
        return download_url, None
    except Exception as e:
        msg = f"GitHub yükleme hatası: {e}"
        print(msg)
        return None, msg

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
    
    # Eski davranış: Ortam değişkenlerinden repo ve token alınıp yükleme denenir
    print("Dosya GitHub'a yükleniyor...")
    env_repo = os.getenv("GITHUB_REPO")
    env_token = os.getenv("GITHUB_TOKEN")
    download_url = None
    if env_repo and env_token:
        download_url, upload_err = upload_to_github_release(
            local_filename,
            parsed_data.get('title', 'Bilinmeyen Makale'),
            env_repo,
            env_token,
        )
    
    if download_url:
        return f"✅ PowerPoint sunumu başarıyla oluşturuldu!\n\n📥 İndirme linki: {download_url}\n\n💡 Bu link kalıcıdır ve herkese açıktır."
    else:
        extra = f"\n\nDetay: {upload_err}" if env_repo and env_token else ""
        return (
            f"✅ PowerPoint sunumu başarıyla oluşturuldu: {local_filename}\n\n"
            f"⚠️ GitHub yükleme servisi şu anda kullanılamıyor. Dosya yerel olarak kaydedildi.{extra}"
        )


def create_graphical_abstract(url: str, github_repo: str, github_token: str) -> str:
    """
    Kullanıcıdan alınan URL, repo (kullaniciadi/repoadi) ve token ile PPTX oluşturur,
    `latest-abstract` release'ine yükler ve herkese açık indirme linkini döndürür.
    """
    print(f"Makale ayrıştırılıyor: {url}")
    parsed_data, error = parse_jama_article(url)
    if error:
        return f"HATA: Makale verileri çekilemedi. Teknik Detay: {error}"

    print("İçeriğe göre tematik ikon seçiliyor...")
    thematic_icon_path = select_thematic_icon(
        parsed_data.get("title", ""), parsed_data.get("keywords", [])
    )

    print("PowerPoint sunumu oluşturuluyor...")
    local_filename = create_presentation(parsed_data, thematic_icon_path)

    print("GitHub release oluşturuluyor ve dosya yükleniyor...")
    download_url, upload_err = upload_to_github_release(
        local_filename,
        parsed_data.get("title", "Bilinmeyen Makale"),
        github_repo,
        github_token,
    )

    if download_url:
        return (
            "✅ PowerPoint sunumu başarıyla oluşturuldu!\n\n"
            f"📥 İndirme linki: {download_url}\n\n"
            "💡 Bu link kalıcıdır ve herkese açıktır."
        )
    return (
        f"✅ PowerPoint sunumu başarıyla oluşturuldu: {local_filename}\n\n"
        f"⚠️ GitHub yükleme başarısız oldu. Repo adını ve token'ı kontrol edin. Detay: {upload_err}"
    )