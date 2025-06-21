"""Test Script for YouTube Playlist Learning Module Generator with Firebase

Quick test script to verify the installation and basic functionality including Firebase.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test if all required packages can be imported."""
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
    firebase_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    if not youtube_key:
        print("❌ YOUTUBE_API_KEY not found")
        print("   Please set your YouTube Data API key in .env file")
        return False
    else:
        print(f"✅ YOUTUBE_API_KEY found (length: {len(youtube_key)})")
    
    if not google_ai_key:
        print("❌ GOOGLE_AI_API_KEY not found")
        print("   Please set your Google AI API key in .env file")
        return False
    else:
        print(f"✅ GOOGLE_AI_API_KEY found (length: {len(google_ai_key)})")
    
    if firebase_path:
        if os.path.exists(firebase_path):
            print(f"✅ FIREBASE_SERVICE_ACCOUNT_PATH found: {firebase_path}")
        else:
            print(f"⚠️  FIREBASE_SERVICE_ACCOUNT_PATH set but file not found: {firebase_path}")
    else:
        print("⚠️  FIREBASE_SERVICE_ACCOUNT_PATH not set (Firebase features will be disabled)")
    
    return True


def test_custom_modules():
    """Test custom modules."""
    print("\n📦 Testing custom modules...")
    
    # Add src directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from src.youtube_extractor import YouTubeExtractor
        print("✅ YouTubeExtractor")
        
        from src.content_analyzer import ContentAnalyzer
        print("✅ ContentAnalyzer")
        
        from src.module_generator import ModuleGenerator
        print("✅ ModuleGenerator")
        
        from src.firebase_service import FirebaseService
        print("✅ FirebaseService")
        
        from src.utils import validate_youtube_url, ProgressTracker
        print("✅ Utils")
        
        return True
        
    except ImportError as e:
        print(f"❌ Custom module import error: {e}")
        return False


def test_firebase_connection():
    """Test Firebase connection."""
    print("\n🔥 Testing Firebase connection...")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from src.firebase_service import FirebaseService
        
        firebase_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        firebase_service = FirebaseService(firebase_path)
        
        if firebase_service.is_connected():
            print("✅ Firebase connected successfully")
            print("   Firestore client initialized")
            return True
        else:
            print("⚠️  Firebase not connected (optional feature)")
            print("   To enable Firebase:")
            print("   1. Create a Firebase project")
            print("   2. Enable Firestore")
            print("   3. Download service account JSON")
            print("   4. Set FIREBASE_SERVICE_ACCOUNT_PATH in .env")
            return True  # This is optional, so not a failure
            
    except Exception as e:
        print(f"⚠️  Firebase connection failed: {e}")
        print("   Firebase features will be disabled")
        return True  # This is optional, so not a failure


def test_url_validation():
    """Test URL validation."""
    print("\n🔗 Testing URL validation...")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from src.utils import validate_youtube_url
        
        # Test valid URLs
        valid_urls = [
            "https://www.youtube.com/playlist?list=PLxxx...",
            "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nu...",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=P..."
        ]
        
        # Test invalid URLs
        invalid_urls = [
            "https://www.google.com...",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ...",
            "not a url...",
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
        print(f"❌ URL validation error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 YouTube Playlist Learning Module Generator - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment),
        ("Custom Modules", test_custom_modules),
        ("Firebase Connection", test_firebase_connection),
        ("URL Validation", test_url_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
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
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file (copy from .env.example)")
        if not os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'):
            print("2. (Optional) Set up Firebase for data persistence")
            print("3. Run 'python main.py --help' to see CLI usage")
            print("4. Run 'python app.py' to start the web interface")
        else:
            print("2. Run 'python main.py --help' to see CLI usage")
            print("3. Run 'python app.py' to start the web interface")
    else:
        print("❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
