#!/usr/bin/env python3
"""
Custom URL Test Script for YouTube Course Generator Agent

This script allows you to easily test the agent with any YouTube playlist URL.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from yt_agent import YouTubeAgent
from dotenv import load_dotenv

def test_custom_url():
    """Test the agent with a custom URL."""
    print("🧪 YouTube Course Generator - Custom URL Test")
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
        return
    
    # Get URL from user
    print("\n📝 Enter your YouTube playlist URL:")
    print("Examples:")
    print("  - https://www.youtube.com/playlist?list=PLxxxxx")
    print("  - https://www.youtube.com/watch?v=xxxxx&list=PLxxxxx")
    print()
    
    playlist_url = input("Playlist URL: ").strip()
    
    if not playlist_url:
        print("❌ No URL provided. Exiting.")
        return
    
    # Get max videos
    try:
        max_videos_input = input("Max videos to process (default: 10): ").strip()
        max_videos = int(max_videos_input) if max_videos_input else 10
    except ValueError:
        max_videos = 10
        print("⚠️  Invalid number, using default (10)")
    
    # Confirm settings
    print(f"\n📋 Test Configuration:")
    print(f"   URL: {playlist_url}")
    print(f"   Max Videos: {max_videos}")
    print(f"   Output: output/ directory")
    
    proceed = input("\nProceed with test? (y/n): ").strip().lower()
    if proceed != 'y':
        print("❌ Test cancelled.")
        return
    
    try:
        print("\n🚀 Starting course generation...")
        print("-" * 60)
        
        # Initialize agent
        agent = YouTubeAgent(youtube_api_key, gemini_api_key, "output")
        
        # Process playlist
        output_file = agent.process_playlist(playlist_url, max_videos)
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Course generated successfully!")
        print(f"📁 Output file: {output_file}")
        
        # Load and display summary
        import json
        with open(output_file, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        print(agent.get_course_summary(course_data))
        
        # Ask if user wants to see the JSON structure
        show_json = input("\nShow JSON structure? (y/n): ").strip().lower()
        if show_json == 'y':
            print("\n📊 Course JSON Structure:")
            print("-" * 30)
            course = course_data.get('course', {})
            modules = course_data.get('modules', [])
            assignments = course_data.get('assignments', [])
            
            print(f"Course Title: {course.get('title')}")
            print(f"Modules: {len(modules)}")
            for i, module in enumerate(modules, 1):
                lessons = module.get('lessons', [])
                print(f"  Module {i}: {module.get('title')} ({len(lessons)} lessons)")
            print(f"Assignments: {len(assignments)}")
            print(f"Final Exam: {'Yes' if course_data.get('finalExam') else 'No'}")
        
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        print("Please check:")
        print("  - Playlist URL is valid and public")
        print("  - API keys are correctly set")
        print("  - Internet connection is stable")

if __name__ == "__main__":
    test_custom_url()
