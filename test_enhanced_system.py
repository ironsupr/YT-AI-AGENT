#!/usr/bin/env python3
"""Test script for the enhanced YouTube Playlist Learning Module Generator."""

import os
import sys
import json
from dotenv import load_dotenv

# Add src directory to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_enhanced_analyzer():
    """Test the enhanced content analyzer."""
    from enhanced_content_analyzer import EnhancedContentAnalyzer
    from youtube_extractor import YouTubeExtractor
    
    # Check for API keys
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    google_ai_api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_api_key or not google_ai_api_key:
        print("❌ Error: Missing required API keys in .env file")
        print("Please ensure you have:")
        print("  - YOUTUBE_API_KEY")
        print("  - GOOGLE_AI_API_KEY")
        return False
    
    try:
        print("🔧 Initializing components...")
        extractor = YouTubeExtractor(youtube_api_key)
        analyzer = EnhancedContentAnalyzer(google_ai_api_key)
        
        # Test with a sample playlist (use a short one for testing)
        test_playlist_url = "https://www.youtube.com/playlist?list=PLWKjhJtqVAbleDe3_ZA8h3AO2rXar-q2V"
        
        print(f"📥 Extracting playlist data from: {test_playlist_url}")
        playlist_data = extractor.extract_playlist_data(test_playlist_url, max_videos=5)
        
        print(f"✅ Extracted {len(playlist_data.get('videos', []))} videos")
        
        print("🧠 Generating enhanced course structure...")
        course_structure = analyzer.generate_comprehensive_course(playlist_data)
        
        # Display results
        course = course_structure.get('course', {})
        modules = course_structure.get('modules', [])
        assignments = course_structure.get('assignments', [])
        final_exam = course_structure.get('finalExam', {})
        
        print("\n" + "="*60)
        print("🎉 ENHANCED COURSE GENERATION SUCCESSFUL!")
        print("="*60)
        print(f"📚 Course Title: {course.get('title', 'N/A')}")
        print(f"🏷️  Category: {course.get('category', 'N/A')}")
        print(f"📈 Level: {course.get('level', 'N/A')}")
        print(f"💰 Price: ${course.get('price', 0)}")
        print(f"⏱️  Duration: {course.get('duration', 'N/A')}")
        print(f"👨‍🏫 Instructor: {course.get('instructor', 'N/A')}")
        print(f"🕐 Estimated Hours: {course.get('estimatedHours', 0)}")
        print(f"📖 Modules: {len(modules)}")
        print(f"📝 Assignments: {len(assignments)}")
        print(f"🎓 Final Exam: {'Yes' if final_exam else 'No'}")
        
        # Show learning objectives
        objectives = course.get('learningObjectives', [])
        if objectives:
            print(f"\n🎯 Learning Objectives:")
            for i, obj in enumerate(objectives, 1):
                print(f"   {i}. {obj}")
        
        # Show modules overview
        if modules:
            print(f"\n📖 Modules Overview:")
            for i, module in enumerate(modules, 1):
                lessons = module.get('lessons', [])
                print(f"   Module {i}: {module.get('title', 'N/A')} ({len(lessons)} lessons)")
        
        # Save to file for inspection
        output_file = "test_enhanced_course.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(course_structure, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full course structure saved to: {output_file}")
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_format():
    """Test that the course structure matches the expected JSON format."""
    print("\n🔍 Testing API format compliance...")
    
    # Check if test file exists
    if not os.path.exists("test_enhanced_course.json"):
        print("❌ Test file not found. Run basic test first.")
        return False
    
    try:
        with open("test_enhanced_course.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required top-level keys
        required_keys = ['course', 'modules', 'assignments', 'finalExam', 'generatedAt']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing required keys: {missing_keys}")
            return False
        
        # Check course structure
        course = data['course']
        course_required = ['title', 'description', 'category', 'level', 'price', 'duration', 
                          'instructor', 'tags', 'thumbnail', 'prerequisites', 'learningObjectives']
        course_missing = [key for key in course_required if key not in course]
        
        if course_missing:
            print(f"❌ Missing course keys: {course_missing}")
            return False
        
        # Check modules structure
        modules = data['modules']
        if modules:
            module = modules[0]
            module_required = ['id', 'title', 'description', 'duration', 'order', 'lessons']
            module_missing = [key for key in module_required if key not in module]
            
            if module_missing:
                print(f"❌ Missing module keys: {module_missing}")
                return False
            
            # Check lessons structure
            lessons = module.get('lessons', [])
            if lessons:
                lesson = lessons[0]
                lesson_required = ['id', 'title', 'description', 'type', 'duration', 'order', 'content']
                lesson_missing = [key for key in lesson_required if key not in lesson]
                
                if lesson_missing:
                    print(f"❌ Missing lesson keys: {lesson_missing}")
                    return False
        
        print("✅ JSON format compliance test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking format: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced YouTube Playlist Learning Module Generator")
    print("="*60)
    
    # Run tests
    test1_passed = test_enhanced_analyzer()
    test2_passed = test_api_format() if test1_passed else False
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    print(f"Enhanced Course Generation: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"JSON Format Compliance: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The enhanced system is ready to use.")
        print("\n🌐 To test the web interface:")
        print("   1. Run: python app.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Select 'Enhanced Course Structure' format")
        print("   4. Enter a YouTube playlist URL")
        print("   5. Click 'Generate Learning Modules'")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if (test1_passed and test2_passed) else 1)
