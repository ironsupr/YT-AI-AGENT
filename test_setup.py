"""Test Script for YouTube Playlist Learning Module Generator

Quick test script to verify the installation and basic functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():    """Test if all required packages can be imported."""
    print("🧪 Testing package imports...")
    try:
        import requests
        print("✅ requests")
        
        from googleapiclient.discovery import build
        print("✅ google-api-python-client")
        
        from youtube_transcript_api import YouTubeTranscriptApi
        print("✅ youtube-transcript-api")
        
        import google.generativeai as genai
        print("✅ google-generativeai")
        
        import firebase_admin
        print("✅ firebase-admin")
        
        from flask import Flask
        print("✅ flask")
        
        import markdown
        print("✅ markdown")
        
        print("\n✅ All packages imported successfully!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


def test_environment():
    """Test environment variables."""
    print("\n🔧 Testing environment configuration...")
    
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    google_ai_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_key:
        print("❌ YOUTUBE_API_KEY not found in environment variables")
        print("   Please add your YouTube Data API key to .env file")
        return False
    else:
        print(f"✅ YOUTUBE_API_KEY found (length: {len(youtube_key)})")
    
    if not google_ai_key:
        print("❌ GOOGLE_AI_API_KEY not found in environment variables")
        print("   Please add your Google AI API key to .env file")
        return False
    else:
        print(f"✅ GOOGLE_AI_API_KEY found (length: {len(google_ai_key)})")
    
    return True


def test_modules():
    """Test custom modules."""
    print("\n📦 Testing custom modules...")
    
    try:
        sys.path.append('src')
        
        from src.youtube_extractor import YouTubeExtractor
        print("✅ YouTubeExtractor")
        
        from src.content_analyzer import ContentAnalyzer
        print("✅ ContentAnalyzer")
        
        from src.module_generator import ModuleGenerator
        print("✅ ModuleGenerator")
        
        from src.utils import validate_youtube_url
        print("✅ Utils")
        
        return True
        
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        return False


def test_youtube_url_validation():
    """Test URL validation."""
    print("\n🔗 Testing URL validation...")
    
    try:
        sys.path.append('src')
        from src.utils import validate_youtube_url
        
        # Test valid URLs
        valid_urls = [
            "https://www.youtube.com/playlist?list=PLxxx",
            "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMfqVYjeQsS2WY1-3k",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxxx"
        ]
        
        # Test invalid URLs
        invalid_urls = [
            "https://www.google.com",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # No playlist
            "not a url",
            ""
        ]
        
        for url in valid_urls:
            if validate_youtube_url(url):
                print(f"✅ Valid URL recognized: {url[:50]}...")
            else:
                print(f"❌ Valid URL rejected: {url[:50]}...")
                return False
        
        for url in invalid_urls:
            if not validate_youtube_url(url):
                print(f"✅ Invalid URL rejected: {url[:50]}...")
            else:
                print(f"❌ Invalid URL accepted: {url[:50]}...")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ URL validation test error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 YouTube Playlist Learning Module Generator - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment),
        ("Custom Modules", test_modules),
        ("URL Validation", test_youtube_url_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file (copy from .env.example)")
        print("2. Run 'python main.py --help' to see CLI usage")
        print("3. Run 'python app.py' to start the web interface")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Make sure you have:")
        print("- Installed all required packages")
        print("- Set up your API keys in .env file")
        print("- Python 3.8+ installed")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
