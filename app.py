"""Flask Web Application

Web interface for the YouTube Playlist Learning Module Generator.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Optional

from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.youtube_extractor import YouTubeExtractor
from src.content_analyzer import ContentAnalyzer
from src.enhanced_content_analyzer import EnhancedContentAnalyzer
from src.module_generator import ModuleGenerator
from src.firebase_service import FirebaseService
from src.utils import validate_youtube_url

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Global variables for components
extractor = None
analyzer = None
enhanced_analyzer = None
generator = None
firebase_service = None


def initialize_components():
    """Initialize application components."""
    global extractor, analyzer, enhanced_analyzer, generator, firebase_service
    
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    google_ai_api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_api_key or not google_ai_api_key:
        raise ValueError("Missing required API keys in environment variables")
    
    extractor = YouTubeExtractor(youtube_api_key)
    analyzer = ContentAnalyzer(google_ai_api_key, os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'))
    enhanced_analyzer = EnhancedContentAnalyzer(google_ai_api_key, os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'))
    generator = ModuleGenerator('output')
    
    # Initialize Firebase (optional)
    try:
        firebase_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        firebase_service = FirebaseService(firebase_path)
        if firebase_service.is_connected():
            logger.info("Firebase connected successfully")
        else:
            logger.info("Firebase not configured (optional)")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}")
        firebase_service = None


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/api/process_playlist', methods=['POST'])
def process_playlist():
    """Process YouTube playlist and generate learning modules."""
    try:
        data = request.get_json()
        playlist_url = data.get('playlist_url', '').strip()
        max_videos = data.get('max_videos', 20)
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400
        
        if not validate_youtube_url(playlist_url):
            return jsonify({'error': 'Invalid YouTube playlist URL'}), 400
        
        # Initialize components if not already done
        if not extractor:
            initialize_components()
          # Process playlist
        logger.info(f"Processing playlist: {playlist_url}")
        
        # Extract playlist ID for Firebase
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(playlist_url)
        playlist_id = parse_qs(parsed_url.query).get('list', [None])[0]
        
        # Check for existing data in Firebase
        existing_analysis = None
        if firebase_service and firebase_service.is_connected() and playlist_id:
            existing_analysis = firebase_service.get_analysis_results(playlist_id)
            if existing_analysis:
                logger.info("Using cached analysis from Firebase")
        
        # Step 1: Extract playlist data
        playlist_data = extractor.extract_playlist_data(playlist_url, max_videos)
        
        # Store playlist data in Firebase
        if firebase_service and firebase_service.is_connected():
            firebase_service.store_playlist(playlist_data)
        
        # Step 2: Analyze content (use cached if available)
        if existing_analysis:
            analysis_results = existing_analysis
        else:
            analysis_results = analyzer.analyze_playlist_content(playlist_data)
            # Store analysis in Firebase
            if firebase_service and firebase_service.is_connected() and playlist_id:
                firebase_service.store_analysis_results(playlist_id, analysis_results)
          # Step 3: Generate learning modules
        course_package = generator.generate_learning_modules(analysis_results)
        
        # Return summary data
        return jsonify({
            'success': True,
            'course_info': course_package['course_info'],
            'modules': course_package['modules'],
            'total_modules': len(course_package['modules']),
            'processing_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing playlist: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_enhanced_course', methods=['POST'])
def generate_enhanced_course():
    """Generate comprehensive course structure using enhanced analyzer."""
    try:
        data = request.get_json()
        playlist_url = data.get('playlist_url', '').strip()
        max_videos = data.get('max_videos', 20)
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400
        
        if not validate_youtube_url(playlist_url):
            return jsonify({'error': 'Invalid YouTube playlist URL'}), 400
        
        # Initialize components if not already done
        if not extractor or not enhanced_analyzer:
            initialize_components()
        
        # Process playlist
        logger.info(f"Generating enhanced course for playlist: {playlist_url}")
        
        # Extract playlist ID for Firebase
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(playlist_url)
        playlist_id = parse_qs(parsed_url.query).get('list', [None])[0]
        
        # Step 1: Extract playlist data
        playlist_data = extractor.extract_playlist_data(playlist_url, max_videos)
        
        # Store playlist data in Firebase if available
        if firebase_service and firebase_service.is_connected():
            firebase_service.store_playlist(playlist_data)
        
        # Step 2: Generate comprehensive course structure
        course_structure = enhanced_analyzer.generate_comprehensive_course(playlist_data)
        
        # Store enhanced course data in Firebase if available
        if firebase_service and firebase_service.is_connected() and playlist_id:
            firebase_service.store_analysis_results(playlist_id, course_structure)
        
        # Return complete course structure
        return jsonify(course_structure)
        
    except Exception as e:
        logger.error(f"Error generating enhanced course: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/validate_url', methods=['POST'])
def validate_url():
    """Validate YouTube playlist URL."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'valid': False, 'error': 'URL is required'})
        
        is_valid = validate_youtube_url(url)
        
        if is_valid and extractor:
            # Try to extract playlist ID to verify it exists
            try:
                playlist_id = extractor.extract_playlist_id(url)
                if playlist_id:
                    playlist_info = extractor.get_playlist_info(playlist_id)
                    return jsonify({
                        'valid': True,
                        'playlist_info': {
                            'title': playlist_info['title'],
                            'video_count': playlist_info['video_count'],
                            'channel': playlist_info['channel_title']
                        }
                    })
            except Exception as e:
                logger.warning(f"Could not fetch playlist info: {e}")
        
        return jsonify({'valid': is_valid})
        
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return jsonify({'valid': False, 'error': str(e)})


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files."""
    try:
        return send_from_directory('output', filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': 'File not found'}), 404


@app.route('/course/<path:filename>')
def view_course(filename):
    """View generated course files."""
    try:
        return send_from_directory('output', filename)
    except Exception as e:
        logger.error(f"Error viewing course file: {e}")
        return jsonify({'error': 'File not found'}), 404


@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check if components are initialized
        if not extractor:
            initialize_components()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'youtube_extractor': extractor is not None,
                'content_analyzer': analyzer is not None,
                'enhanced_analyzer': enhanced_analyzer is not None,
                'module_generator': generator is not None
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/playlists', methods=['GET'])
def list_playlists():
    """List all stored playlists from Firebase."""
    try:
        if not firebase_service or not firebase_service.is_connected():
            return jsonify({'error': 'Firebase not configured'}), 503
        
        limit = request.args.get('limit', 50, type=int)
        playlists = firebase_service.list_playlists(limit)
        
        return jsonify({
            'success': True,
            'playlists': playlists,
            'count': len(playlists)
        })
        
    except Exception as e:
        logger.error(f"Error listing playlists: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlists/search', methods=['GET'])
def search_playlists():
    """Search playlists in Firebase."""
    try:
        if not firebase_service or not firebase_service.is_connected():
            return jsonify({'error': 'Firebase not configured'}), 503
        
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        limit = request.args.get('limit', 20, type=int)
        playlists = firebase_service.search_playlists(query, limit)
        
        return jsonify({
            'success': True,
            'playlists': playlists,
            'count': len(playlists),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error searching playlists: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlists/<playlist_id>', methods=['GET'])
def get_playlist_details(playlist_id):
    """Get detailed playlist information from Firebase."""
    try:
        if not firebase_service or not firebase_service.is_connected():
            return jsonify({'error': 'Firebase not configured'}), 503
        
        playlist_data = firebase_service.get_playlist(playlist_id)
        if not playlist_data:
            return jsonify({'error': 'Playlist not found'}), 404
        
        # Also get analysis if available
        analysis_data = firebase_service.get_analysis_results(playlist_id)
        
        return jsonify({
            'success': True,
            'playlist': playlist_data,
            'analysis': analysis_data
        })
        
    except Exception as e:
        logger.error(f"Error getting playlist details: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlists/<playlist_id>/videos', methods=['GET'])
def get_playlist_videos(playlist_id):
    """Get all videos in a playlist from Firebase."""
    try:
        if not firebase_service or not firebase_service.is_connected():
            return jsonify({'error': 'Firebase not configured'}), 503
        
        playlist_data = firebase_service.get_playlist(playlist_id)
        if not playlist_data:
            return jsonify({'error': 'Playlist not found'}), 404
        
        videos = playlist_data.get('videos', [])
        
        return jsonify({
            'success': True,
            'playlist_id': playlist_id,
            'playlist_title': playlist_data.get('title', ''),
            'videos': videos,
            'count': len(videos)
        })
        
    except Exception as e:
        logger.error(f"Error getting playlist videos: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlists/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """Delete a playlist from Firebase."""
    try:
        if not firebase_service or not firebase_service.is_connected():
            return jsonify({'error': 'Firebase not configured'}), 503
        
        success = firebase_service.delete_playlist(playlist_id)
        if not success:
            return jsonify({'error': 'Failed to delete playlist'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Playlist deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting playlist: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/firebase/status', methods=['GET'])
def firebase_status():
    """Check Firebase connection status."""
    try:
        connected = firebase_service and firebase_service.is_connected()
        
        return jsonify({
            'connected': connected,
            'service_available': firebase_service is not None
        })
        
    except Exception as e:
        logger.error(f"Error checking Firebase status: {e}", exc_info=True)
        return jsonify({
            'connected': False,
            'service_available': False,
            'error': str(e)
        })


@app.route('/api/playlists/<playlist_id>/links', methods=['GET'])
def get_playlist_video_links(playlist_id):
    """Get just the video links from a playlist."""
    try:
        if not firebase_service or not firebase_service.is_connected():
            return jsonify({'error': 'Firebase not configured'}), 503
        
        video_links = firebase_service.get_playlist_video_links(playlist_id)
        if not video_links:
            return jsonify({'error': 'Playlist not found or no videos'}), 404
        
        # Create simple link list
        simple_links = [video['url'] for video in video_links]
        
        return jsonify({
            'success': True,
            'playlist_id': playlist_id,
            'video_links': simple_links,
            'detailed_links': video_links,
            'count': len(video_links)
        })
        
    except Exception as e:
        logger.error(f"Error getting playlist video links: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    try:
        # Initialize components on startup
        initialize_components()
        logger.info("Components initialized successfully")
        
        # Run the Flask app
        debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        port = int(os.getenv('FLASK_PORT', 5000))
        
        print(f"🚀 Starting YouTube Playlist Learning Module Generator Web App")
        print(f"🌐 Open http://localhost:{port} in your browser")
        print(f"🔧 Debug mode: {debug_mode}")
        
        app.run(debug=debug_mode, port=port, host='0.0.0.0')
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"❌ Error: {e}")
        print("Please check your .env file contains the required API keys:")
        print("  - YOUTUBE_API_KEY")
        print("  - OPENAI_API_KEY")
        sys.exit(1)
