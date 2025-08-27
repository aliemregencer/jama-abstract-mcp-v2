# JAMA VA Abstract Generator

Bu MCP (Model Context Protocol) sunucusu, JAMA Network makalelerinden Veterans Affairs (VA) formatında görsel özetler oluşturur ve bunları GitHub release olarak yükler.

## Özellikler

- **JAMA Network Makale Parsing**: Çoklu scraping yöntemi ile güvenilir içerik çekme
- **VA Template Kullanımı**: `templates/jama_va.pptx` şablonunu kullanarak tutarlı format
- **Akıllı İçerik Yerleştirme**: Şekil isimlerine göre otomatik içerik dağıtımı
- **GitHub Integration**: Otomatik release oluşturma ve dosya yükleme
- **MCP Protocol**: Standart MCP araçları ile entegrasyon
- **Container Ready**: Docker container ortamında tam uyumlu çalışma

## Scraping Yöntemleri

Sistem, JAMA Network makalelerini çekmek için çoklu yöntem kullanır:

1. **Requests (Öncelikli)**: Hızlı ve güvenilir HTTP istekleri
2. **Selenium (Yedek)**: JavaScript gerektiren sayfalar için
3. **Fallback Requests**: Selenium başarısız olursa son çare

### Container Ortamı Desteği

- Google Chrome otomatik kurulum
- ChromeDriver otomatik yönetimi
- Headless mode desteği
- Memory ve GPU optimizasyonları

## Kurulum

### Gereksinimler

```bash
pip install -r requirements.txt
```

### Ortam Değişkenleri

```bash
export GITHUB_REPO="kullanici/repoadi"
export GITHUB_TOKEN="ghp_your_github_token_here"
```

## Kullanım

### MCP Tool Olarak

```python
# MCP client'ta
result = await mcp.generate_va_abstract(
    url="https://jamanetwork.com/journals/jamanetworkopen/article-abstract/...",
    github_repo="kullanici/repoadi",
    github_token="ghp_..."
)
```

### Doğrudan Python

```python
from app import create_graphical_abstract

result = create_graphical_abstract(
    url="https://jamanetwork.com/...",
    github_repo="kullanici/repoadi",
    github_token="ghp_..."
)
print(result)
```

## Template Yapısı

`templates/jama_va.pptx` dosyası aşağıdaki şekil isimlerini içerir:

- `title`: Makale başlığı
- `population_subtitle`: Popülasyon alt başlığı
- `population_description`: Popülasyon açıklaması
- `intervention_subtitle`: Müdahale alt başlığı
- `intervention_description`: Müdahale açıklaması
- `settings_locations_description`: Ayarlar ve konumlar
- `primary_outcome_description`: Birincil sonuç
- `findings_description_1` & `findings_description_2`: Bulgular (2 parça)
- `footer_citation`: Alt bilgi alıntısı

## Çıktı

- **Dosya**: `JAMA_VA_Abstract.pptx`
- **GitHub Release**: `latest-abstract` tag'i ile
- **İndirme Linki**: Herkese açık, kalıcı link

## Smithery Deployment

Bu proje Smithery'de deploy edilmiştir ve MCP sunucusu olarak çalışır.

### Konfigürasyon

```yaml
runtime: "container"
startCommand:
  type: "http"
  command: "python"
  args: ["-m", "server"]
```

### Endpoint

- **Port**: 8000 (varsayılan)
- **MCP Endpoint**: `/mcp`
- **Transport**: HTTP

## Hata Yönetimi

- JAMA URL doğrulama
- Template dosya kontrolü
- GitHub API hata yakalama
- Selenium hata yönetimi

## Geliştirme

### Test

```bash
python test_app.py
python test_mcp.py
```

### Yerel Çalıştırma

```bash
python -m server
```

## Lisans

Bu proje açık kaynak kodludur.

