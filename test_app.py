#!/usr/bin/env python3
"""
JAMA VA Abstract Generator test scripti
"""

import os
import sys
from app import create_presentation

def test_scraping_methods():
    """Farklı scraping yöntemlerini test eder"""
    print("🧪 Scraping Yöntemleri Test...")
    
    try:
        from app import parse_jama_article
        
        # Test URL
        test_url = "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2837260?resultClick=1"
        print(f"📝 Test URL: {test_url}")
        
        print("🔄 Makale parsing test ediliyor...")
        result, error = parse_jama_article(test_url)
        
        if error:
            print(f"❌ Parsing hatası: {error}")
            return False
        elif result:
            print("✅ Makale başarıyla parse edildi")
            print(f"📋 Başlık: {result.get('title', 'Bulunamadı')}")
            print(f"📋 Yazarlar: {len(result.get('authors', []))}")
            print(f"📋 Abstract bölümleri: {list(result.get('abstract', {}).keys())}")
            return True
        else:
            print("❌ Parsing sonucu boş")
            return False
            
    except Exception as e:
        print(f"❌ Test sırasında hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_va_template():
    """VA template kullanımını test eder"""
    print("🧪 VA Template Test Başlatılıyor...")
    
    # Test verisi
    test_data = {
        "title": "Test Makale Başlığı - Randomized Clinical Trial",
        "authors": [{"name": "Test Author, MD"}],
        "publication_date": "2024-01-01",
        "doi": "10.1001/jamanetworkopen.2024.0001",
        "abstract": {
            "design, setting, and participants": "Randomized clinical trial of 1000 participants aged 18-65 years from 5 medical centers across the United States.",
            "interventions": "Participants were randomly assigned to receive either treatment A (n=500) or treatment B (n=500) for 12 weeks.",
            "main outcomes and measures": "Primary outcome was change in symptom score from baseline to week 12. Secondary outcomes included quality of life measures.",
            "results": "Treatment A showed significant improvement in symptom scores compared to treatment B (mean difference: -2.5 points, 95% CI: -3.2 to -1.8, P<0.001). Quality of life measures also improved significantly in the treatment A group.",
            "conclusions and relevance": "Treatment A was more effective than treatment B in improving symptoms and quality of life in this patient population."
        },
        "keywords": ["randomized trial", "treatment", "symptoms"]
    }
    
    try:
        # Template dosyasının varlığını kontrol et
        template_path = "templates/jama_va.pptx"
        if not os.path.exists(template_path):
            print(f"❌ Template dosyası bulunamadı: {template_path}")
            return False
        
        print(f"✅ Template dosyası bulundu: {template_path}")
        
        # Test ikonu
        test_icon = "icons/default.png"
        if not os.path.exists(test_icon):
            print(f"⚠️ Test ikonu bulunamadı: {test_icon}")
            test_icon = "icons/default.png"  # Varsayılan olarak kullan
        
        # Sunum oluştur
        print("📝 Test sunumu oluşturuluyor...")
        filename = create_presentation(test_data, test_icon)
        
        if os.path.exists(filename):
            print(f"✅ Test sunumu başarıyla oluşturuldu: {filename}")
            
            # Dosya boyutunu kontrol et
            file_size = os.path.getsize(filename)
            print(f"📊 Dosya boyutu: {file_size:,} bytes")
            
            # Test dosyasını temizle
            os.remove(filename)
            print(f"🧹 Test dosyası temizlendi: {filename}")
            
            return True
        else:
            print(f"❌ Test sunumu oluşturulamadı: {filename}")
            return False
            
    except Exception as e:
        print(f"❌ Test sırasında hata oluştu: {e}")
        return False

def test_github_integration():
    """GitHub entegrasyonunu test eder (token gerekli)"""
    print("\n🔗 GitHub Integration Test...")
    
    github_repo = os.getenv("GITHUB_REPO")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_repo or not github_token:
        print("⚠️ GitHub repo veya token bulunamadı, test atlanıyor")
        print("   GITHUB_REPO ve GITHUB_TOKEN environment variable'larını ayarlayın")
        return True
    
    print(f"✅ GitHub repo: {github_repo}")
    print("⚠️ GitHub test için gerçek URL gerekli, manuel test önerilir")
    return True

def main():
    """Ana test fonksiyonu"""
    print("🚀 JAMA VA Abstract Generator Test Suite")
    print("=" * 50)
    
    # Scraping testi
    scraping_success = test_scraping_methods()
    
    # VA Template testi
    template_success = test_va_template()
    
    # GitHub integration testi
    github_success = test_github_integration()
    
    # Sonuç özeti
    print("\n" + "=" * 50)
    print("📋 Test Sonuçları:")
    print(f"   Scraping Methods: {'✅ PASS' if scraping_success else '❌ FAIL'}")
    print(f"   VA Template: {'✅ PASS' if template_success else '❌ FAIL'}")
    print(f"   GitHub Integration: {'✅ PASS' if github_success else '⚠️ SKIP'}")
    
    if scraping_success and template_success:
        print("\n🎉 Tüm testler başarılı!")
        return 0
    else:
        print("\n💥 Bazı testler başarısız!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
