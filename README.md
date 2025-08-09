# JAMA Abstract Generator MCP

Bu proje, JAMA Network Open makalelerini parse ederek görsel özet PowerPoint dosyaları oluşturan bir MCP (Model Context Protocol) sunucusudur.

## Özellikler

- JAMA Network Open makalelerini otomatik olarak parse eder
- Makale içeriğine göre tematik ikon seçer
- Profesyonel PowerPoint sunumu oluşturur
- GitHub Releases üzerinden dosya paylaşımı
- MCP protokolü ile entegrasyon

## Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 2. GitHub Token Ayarlayın (Opsiyonel)

Dosyaları GitHub Releases üzerinden paylaşmak için:

1. GitHub'da Personal Access Token oluşturun:
   - GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - "Generate new token" → "Generate new token (classic)"
   - Token'a şu izinleri verin:
     - `repo` (tam repository erişimi)
     - `public_repo` (public repository'ler için)

2. Token'ı environment variable olarak ayarlayın:

**Windows:**
```cmd
set GITHUB_TOKEN=your_token_here
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN=your_token_here
```

**PowerShell:**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

### 3. Repository Ayarlarını Güncelleyin

`app.py` dosyasında şu değişkenleri kendi bilgilerinizle güncelleyin:

```python
repo_owner = "your_github_username"  # GitHub kullanıcı adınız
repo_name = "your_repo_name"         # Repository adınız
```

## Kullanım

### MCP Sunucusu Olarak

```bash
python server.py
```

### Doğrudan Test

```bash
python test_app.py
```

## API Kullanımı

MCP sunucusu çalıştığında, şu tool'u kullanabilirsiniz:

```json
{
  "name": "generate_graphical_abstract",
  "description": "Bir JAMA Network Open makale URL'si alır ve makalenin görsel özetini içeren bir PowerPoint (PPTX) dosyası oluşturur.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "JAMA Network Open makale URL'si"
      }
    },
    "required": ["url"]
  }
}
```

## Örnek Kullanım

```
URL: https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2837260?resultClick=1
```

Bu URL'yi MCP sunucusuna gönderdiğinizde:

1. Makale parse edilir
2. İçeriğe göre tematik ikon seçilir
3. PowerPoint sunumu oluşturulur
4. GitHub Releases'e yüklenir (token varsa)
5. İndirme linki döndürülür

## Çıktı Formatı

### Başarılı Durumda:
```
✅ PowerPoint sunumu başarıyla oluşturuldu!

📥 İndirme linki: https://github.com/username/repo/releases/download/latest-abstract/JAMA_Graphical_Abstract.pptx

💡 Bu link kalıcıdır ve herkese açıktır.
```

### GitHub Token Yoksa:
```
✅ PowerPoint sunumu başarıyla oluşturuldu: JAMA_Graphical_Abstract.pptx

⚠️ GitHub yükleme servisi şu anda kullanılamıyor. Dosya yerel olarak kaydedildi.
```

## Dosya Yapısı

```
abstract-mcp/
├── app.py              # Ana uygulama
├── server.py           # MCP sunucusu
├── parser.py           # HTML parsing fonksiyonları
├── requirements.txt    # Bağımlılıklar
├── mcp.yaml           # MCP konfigürasyonu
├── icons/             # Tematik ikonlar
│   ├── cardiology.png
│   ├── neurology.png
│   ├── oncology.png
│   ├── public_health.png
│   └── default.png
├── jama_logo.png      # JAMA logosu
└── test_app.py        # Test scripti
```

## Tematik İkonlar

Sistem makale içeriğine göre otomatik olarak şu ikonları seçer:

- **Cardiology**: Kalp, kardiyoloji ile ilgili makaleler
- **Neurology**: Beyin, nöroloji ile ilgili makaleler  
- **Oncology**: Kanser, onkoloji ile ilgili makaleler
- **Public Health**: Halk sağlığı, epidemiyoloji ile ilgili makaleler
- **Default**: Diğer tüm makaleler

## Hata Yönetimi

Sistem şu durumlarda graceful fallback yapar:

- GitHub token yoksa → Yerel dosya kaydeder
- Network hatası → Hata mesajı döndürür
- Parsing hatası → Detaylı hata mesajı döndürür

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

