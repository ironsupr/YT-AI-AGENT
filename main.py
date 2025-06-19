"""Main CLI Application

Command-line interface for the YouTube Playlist Learning Module Generator.
"""

import os
import sys
import argparse
import logging
from typing import Optional
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.youtube_extractor import YouTubeExtractor
from src.content_analyzer import ContentAnalyzer
from src.module_generator import ModuleGenerator
from src.firebase_service import FirebaseService
from src.utils import validate_youtube_url, ProgressTracker

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='Generate learning modules from YouTube playlists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "https://www.youtube.com/playlist?list=PLxxx"
  python main.py --url "playlist_url" --max-videos 20 --output "./my_course"
        """
    )
    
    parser.add_argument(
        'playlist_url',
        nargs='?',
        help='YouTube playlist URL'
    )
    
    parser.add_argument(
        '--url',
        help='YouTube playlist URL (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--max-videos',
        type=int,
        default=50,
        help='Maximum number of videos to process (default: 50)'    )
    
    parser.add_argument(
        '--output',
        default='output',
        help='Output directory for generated modules (default: output)'
    )
    
    parser.add_argument(
        '--model',
        default='gemini-1.5-flash',
        help='Gemini model to use (default: gemini-1.5-flash)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get playlist URL
    playlist_url = args.playlist_url or args.url
    if not playlist_url:
        print("Error: Please provide a YouTube playlist URL")
        parser.print_help()
        sys.exit(1)
      # Validate URL
    if not validate_youtube_url(playlist_url):
        print("Error: Invalid YouTube playlist URL")
        print("Please provide a URL like: https://www.youtube.com/playlist?list=PLxxx")
        sys.exit(1)
      # Check for required API keys
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    google_ai_api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        print("Please set your YouTube Data API key in a .env file")
        sys.exit(1)
    
    if not google_ai_api_key:
        print("Error: GOOGLE_AI_API_KEY not found in environment variables")
        print("Please set your Google AI API key in a .env file")
        sys.exit(1)
    
    try:
        # Initialize components
        print(f"🚀 Starting YouTube Playlist Learning Module Generator")
        print(f"📋 Playlist URL: {playlist_url}")
        print(f"📁 Output Directory: {args.output}")
        print(f"🎯 Max Videos: {args.max_videos}\n")
        
        extractor = YouTubeExtractor(youtube_api_key)
        analyzer = ContentAnalyzer(google_ai_api_key, args.model)
        generator = ModuleGenerator(args.output)
        
        # Initialize Firebase (optional)
        firebase_service = None
        firebase_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        try:
            firebase_service = FirebaseService(firebase_path)
            if firebase_service.is_connected():
                print("🔥 Firebase connected successfully")
            else:
                print("⚠️  Firebase not configured (optional)")
        except Exception as e:
            print(f"⚠️  Firebase initialization failed: {e}")
        
        # Extract playlist ID for Firebase storage
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(playlist_url)
        playlist_id = parse_qs(parsed_url.query).get('list', [None])[0]
        
        # Check if playlist already exists in Firebase
        existing_playlist = None
        if firebase_service and firebase_service.is_connected() and playlist_id:
            existing_playlist = firebase_service.get_playlist_summary(playlist_id)
            if existing_playlist:
                print(f"📚 Found existing playlist in database: {existing_playlist['title']}")
        
        # Step 1: Extract playlist data
        print("📥 Step 1: Extracting playlist data...")
        playlist_data = extractor.extract_playlist_data(playlist_url, args.max_videos)
        
        print(f"✅ Extracted {playlist_data['total_videos']} videos")
        print(f"📝 {playlist_data['videos_with_transcripts']} videos have transcripts")
        
        # Store playlist data in Firebase
        if firebase_service and firebase_service.is_connected():
            stored_id = firebase_service.store_playlist(playlist_data)
            if stored_id:
                print(f"🔥 Playlist data stored in Firebase with ID: {stored_id}")
        
        print()
        
        # Step 2: Analyze content
        print("🧠 Step 2: Analyzing content with AI...")
        
        # Check for existing analysis in Firebase
        existing_analysis = None
        if firebase_service and firebase_service.is_connected() and playlist_id:
            existing_analysis = firebase_service.get_analysis_results(playlist_id)
            if existing_analysis:
                print("📚 Found existing analysis in database, using cached results")
                analysis_results = existing_analysis
            else:
                analysis_results = analyzer.analyze_playlist_content(playlist_data)
                # Store analysis results
                firebase_service.store_analysis_results(playlist_id, analysis_results)
                print("🔥 Analysis results stored in Firebase")
        else:
            analysis_results = analyzer.analyze_playlist_content(playlist_data)
        
        print(f"✅ Analysis complete")
        print(f"📚 Subject: {analysis_results.get('structure_analysis', {}).get('subject', 'Unknown')}")
        print(f"🎯 Difficulty: {analysis_results.get('difficulty_level', 'Unknown')}")
        print(f"⏱️  Estimated Time: {analysis_results.get('estimated_completion_time', 'Unknown')}\n")
        
        # Step 3: Generate learning modules
        print("📖 Step 3: Generating learning modules...")
        course_package = generator.generate_learning_modules(analysis_results)
        
        print(f"✅ Generated {len(course_package['modules'])} learning modules")
        print(f"📄 Course materials saved to: {args.output}")
        
        # Display summary
        print("\n" + "="*60)
        print("🎉 COURSE GENERATION COMPLETE!")
        print("="*60)
        
        course_info = course_package['course_info']
        print(f"📚 Course Title: {course_info['title']}")
        print(f"📊 Total Modules: {course_info['total_modules']}")
        print(f"🎥 Total Videos: {course_info['total_videos']}")
        print(f"⏱️  Estimated Completion Time: {course_info['estimated_time']}")
        print(f"📈 Difficulty Level: {course_info['difficulty_level']}")
        
        print(f"\n📁 Generated Files:")
        print(f"   • {os.path.join(args.output, 'course_data.json')} - Complete course data")
        print(f"   • {os.path.join(args.output, 'course_guide.html')} - Interactive HTML guide")
        print(f"   • {os.path.join(args.output, 'course_guide.md')} - Markdown guide")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Open the HTML guide in your browser for interactive learning")
        print(f"   2. Use the JSON data to integrate with learning management systems")
        print(f"   3. Customize the modules based on your specific needs")
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        print(f"\n❌ Error occurred: {str(e)}")
        print("Check the logs for more details")
        sys.exit(1)


def test_connection():
    """Test API connections."""
    print("🔧 Testing API connections...")
    
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    google_ai_api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_api_key or not google_ai_api_key:
        print("❌ Missing API keys in environment variables")
        return False
    
    try:
        # Test YouTube API
        extractor = YouTubeExtractor(youtube_api_key)
        test_url = "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMfqVYjeQsS2WY1-3k"
        playlist_id = extractor.extract_playlist_id(test_url)
        if playlist_id:
            print("✅ YouTube API connection successful")
        else:
            print("❌ YouTube API test failed")
            return False
        
        # Test Gemini API
        analyzer = ContentAnalyzer(google_ai_api_key)
        print("✅ Gemini API connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Check if this is a connection test
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = test_connection()
        sys.exit(0 if success else 1)
    
    main()
