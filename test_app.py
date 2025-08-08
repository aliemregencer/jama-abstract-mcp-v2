#!/usr/bin/env python3
"""
Test script for JAMA Abstract Generator
"""

from app import create_graphical_abstract_from_url

def test_jama_article():
    """Test the JAMA article parsing and presentation generation"""
    
    # Test URL
    test_url = "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2837260?resultClick=1"
    
    print("Testing JAMA Abstract Generator...")
    print(f"URL: {test_url}")
    print("-" * 50)
    
    try:
        result = create_graphical_abstract_from_url(test_url)
        print("RESULT:")
        print(result)
        print("-" * 50)
        
        if "HATA" in result:
            print("❌ Test failed - Error occurred")
            return False
        else:
            print("✅ Test successful - Presentation created")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    test_jama_article()
