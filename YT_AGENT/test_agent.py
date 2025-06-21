#!/usr/bin/env python3
"""
Test script for YouTube Course Generator Agent

This script runs basic tests to ensure the agent is working correctly.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from yt_agent import YouTubeAgent
from dotenv import load_dotenv

def test_agent():
    """Test the YouTube agent with sample data."""
    print("🧪 Testing YouTube Course Generator Agent...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv("../.env")
    
    # Check API keys
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    gemini_api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_api_key or not gemini_api_key:
        print("❌ Missing API keys. Please set:")
        print("  - YOUTUBE_API_KEY")
        print("  - GOOGLE_AI_API_KEY")
        return False
    
    print("✅ API keys found")
    
    # Test with a small public playlist
    test_playlist = "https://www.youtube.com/playlist?list=PLZlA0Gpn_vH_uZs4vJMIhcinABSTUH2bY"
    max_videos = 3
    
    try:
        print(f"🎯 Testing with playlist: {test_playlist}")
        print(f"📊 Max videos: {max_videos}")
        
        # Initialize agent
        agent = YouTubeAgent(youtube_api_key, gemini_api_key, "test_output")
        
        # Process playlist
        output_file = agent.process_playlist(test_playlist, max_videos)
        
        # Verify output file
        if os.path.exists(output_file):
            print(f"✅ Output file created: {output_file}")
            
            # Load and verify JSON structure
            with open(output_file, 'r', encoding='utf-8') as f:
                course_data = json.load(f)
            
            # Basic structure validation
            required_keys = ['course', 'modules', 'assignments', 'finalExam', 'metadata']
            missing_keys = [key for key in required_keys if key not in course_data]
            
            if missing_keys:
                print(f"❌ Missing keys in output: {missing_keys}")
                return False
            
            print("✅ JSON structure is valid")
            
            # Print summary
            course = course_data.get('course', {})
            modules = course_data.get('modules', [])
            
            print(f"✅ Generated course: {course.get('title', 'N/A')}")
            print(f"✅ Modules created: {len(modules)}")
            print(f"✅ Total lessons: {sum(len(m.get('lessons', [])) for m in modules)}")
            
            # Clean up test file
            os.remove(output_file)
            print("🧹 Test file cleaned up")
            
            return True
            
        else:
            print("❌ Output file not created")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Run the test."""
    success = test_agent()
    
    if success:
        print("\n🎉 All tests passed! The agent is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the agent configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
