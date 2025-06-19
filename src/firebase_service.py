"""Firebase Firestore Service Module

This module handles all Firebase Firestore operations for storing and retrieving
playlist data, video information, and analysis results.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirebaseService:
    """Handles Firebase Firestore operations for playlist data management."""
    
    def __init__(self, service_account_path: Optional[str] = None):
        """Initialize Firebase service.
        
        Args:
            service_account_path: Path to Firebase service account JSON file
        """
        self.db = None
        self._initialize_firebase(service_account_path)
    
    def _initialize_firebase(self, service_account_path: Optional[str] = None):
        """Initialize Firebase Admin SDK.
        
        Args:
            service_account_path: Path to service account JSON file
        """
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                if service_account_path and os.path.exists(service_account_path):
                    # Initialize with service account file
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with service account file")
                else:
                    # Try to initialize with default credentials or environment variable
                    try:
                        # This will use Application Default Credentials or GOOGLE_APPLICATION_CREDENTIALS
                        firebase_admin.initialize_app()
                        logger.info("Firebase initialized with default credentials")
                    except Exception as e:
                        logger.warning(f"Could not initialize Firebase: {e}")
                        self.db = None
                        return
            
            # Get Firestore client
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if Firebase connection is available.
        
        Returns:
            True if connected, False otherwise
        """
        return self.db is not None
    
    def store_playlist(self, playlist_data: Dict) -> Optional[str]:
        """Store playlist data in Firestore.
        
        Args:
            playlist_data: Complete playlist data from YouTubeExtractor
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot store playlist")
            return None
        
        try:
            playlist_info = playlist_data['playlist_info']
            playlist_id = playlist_info['id']
            
            # Prepare playlist document
            playlist_doc = {
                'playlist_id': playlist_id,
                'title': playlist_info['title'],
                'description': playlist_info['description'],
                'thumbnail_url': playlist_info['thumbnail'],
                'channel_title': playlist_info['channel_title'],
                'channel_id': playlist_info['channel_id'],
                'video_count': len(playlist_data['videos']),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'url': f"https://www.youtube.com/playlist?list={playlist_id}"
            }
            
            # Store playlist document
            doc_ref = self.db.collection('playlists').document(playlist_id)
            doc_ref.set(playlist_doc)
            
            # Store videos subcollection
            videos_ref = doc_ref.collection('videos')
            for video in playlist_data['videos']:
                video_doc = {
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'description': video.get('description', ''),
                    'thumbnail_url': video.get('thumbnail', ''),
                    'duration': video.get('duration', ''),
                    'published_at': video.get('published_at', ''),
                    'position': video.get('position', 0),
                    'url': f"https://www.youtube.com/watch?v={video['video_id']}",
                    'has_transcript': bool(video.get('transcript')),
                    'transcript_length': len(video.get('transcript', '')),
                    'added_at': datetime.utcnow()
                }
                videos_ref.document(video['video_id']).set(video_doc)
            
            logger.info(f"Stored playlist {playlist_id} with {len(playlist_data['videos'])} videos")
            return playlist_id
            
        except Exception as e:
            logger.error(f"Error storing playlist: {e}")
            return None
    
    def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Retrieve playlist data from Firestore.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Playlist data if found, None otherwise
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot retrieve playlist")
            return None
        
        try:
            # Get playlist document
            doc_ref = self.db.collection('playlists').document(playlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.info(f"Playlist {playlist_id} not found in database")
                return None
            
            playlist_data = doc.to_dict()
            
            # Get videos subcollection
            videos_ref = doc_ref.collection('videos')
            videos_docs = videos_ref.order_by('position').stream()
            
            videos = []
            for video_doc in videos_docs:
                video_data = video_doc.to_dict()
                videos.append(video_data)
            
            playlist_data['videos'] = videos
            
            logger.info(f"Retrieved playlist {playlist_id} with {len(videos)} videos")
            return playlist_data
            
        except Exception as e:
            logger.error(f"Error retrieving playlist: {e}")
            return None
    
    def store_analysis_results(self, playlist_id: str, analysis_data: Dict) -> bool:
        """Store AI analysis results in Firestore.
        
        Args:
            playlist_id: YouTube playlist ID
            analysis_data: Analysis results from ContentAnalyzer
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot store analysis")
            return False
        
        try:
            # Prepare analysis document
            analysis_doc = {
                'playlist_id': playlist_id,
                'content_summary': analysis_data.get('content_summary', ''),
                'structure_analysis': analysis_data.get('structure_analysis', {}),
                'learning_objectives': analysis_data.get('learning_objectives', []),
                'prerequisites': analysis_data.get('prerequisites', []),
                'learning_path': analysis_data.get('learning_path', []),
                'difficulty_level': analysis_data.get('difficulty_level', 'intermediate'),
                'estimated_completion_time': analysis_data.get('estimated_completion_time', 0),
                'video_analyses': analysis_data.get('video_analyses', []),
                'analyzed_at': datetime.utcnow()
            }
            
            # Store analysis document
            doc_ref = self.db.collection('analyses').document(playlist_id)
            doc_ref.set(analysis_doc)
            
            logger.info(f"Stored analysis results for playlist {playlist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            return False
    
    def get_analysis_results(self, playlist_id: str) -> Optional[Dict]:
        """Retrieve AI analysis results from Firestore.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Analysis results if found, None otherwise
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot retrieve analysis")
            return None
        
        try:
            doc_ref = self.db.collection('analyses').document(playlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.info(f"Analysis for playlist {playlist_id} not found in database")
                return None
            
            analysis_data = doc.to_dict()
            logger.info(f"Retrieved analysis results for playlist {playlist_id}")
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            return None
    
    def list_playlists(self, limit: int = 50) -> List[Dict]:
        """List all stored playlists.
        
        Args:
            limit: Maximum number of playlists to return
            
        Returns:
            List of playlist summaries
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot list playlists")
            return []
        
        try:
            playlists_ref = self.db.collection('playlists')
            docs = playlists_ref.order_by('updated_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            playlists = []
            for doc in docs:
                playlist_data = doc.to_dict()
                summary = {
                    'playlist_id': playlist_data['playlist_id'],
                    'title': playlist_data['title'],
                    'thumbnail_url': playlist_data['thumbnail_url'],
                    'video_count': playlist_data['video_count'],
                    'channel_title': playlist_data['channel_title'],
                    'url': playlist_data['url'],
                    'updated_at': playlist_data['updated_at']
                }
                playlists.append(summary)
            
            logger.info(f"Retrieved {len(playlists)} playlists from database")
            return playlists
            
        except Exception as e:
            logger.error(f"Error listing playlists: {e}")
            return []
    
    def search_playlists(self, query: str, limit: int = 20) -> List[Dict]:
        """Search playlists by title or description.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching playlists
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot search playlists")
            return []
        
        try:
            # Note: Firestore doesn't support full-text search natively
            # This is a simple case-insensitive search on title
            query_lower = query.lower()
            
            playlists_ref = self.db.collection('playlists')
            docs = playlists_ref.limit(100).stream()  # Get more docs to filter
            
            matching_playlists = []
            for doc in docs:
                playlist_data = doc.to_dict()
                title = playlist_data.get('title', '').lower()
                description = playlist_data.get('description', '').lower()
                
                if query_lower in title or query_lower in description:
                    summary = {
                        'playlist_id': playlist_data['playlist_id'],
                        'title': playlist_data['title'],
                        'thumbnail_url': playlist_data['thumbnail_url'],
                        'video_count': playlist_data['video_count'],
                        'channel_title': playlist_data['channel_title'],
                        'url': playlist_data['url'],
                        'updated_at': playlist_data['updated_at']
                    }
                    matching_playlists.append(summary)
                    
                    if len(matching_playlists) >= limit:
                        break
            
            logger.info(f"Found {len(matching_playlists)} playlists matching '{query}'")
            return matching_playlists
            
        except Exception as e:
            logger.error(f"Error searching playlists: {e}")
            return []
    
    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete playlist and all associated data.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, cannot delete playlist")
            return False
        
        try:
            # Delete videos subcollection
            playlist_ref = self.db.collection('playlists').document(playlist_id)
            videos_ref = playlist_ref.collection('videos')
            
            # Delete all videos
            videos_docs = videos_ref.stream()
            for video_doc in videos_docs:
                video_doc.reference.delete()
            
            # Delete playlist document
            playlist_ref.delete()
            
            # Delete analysis if exists
            analysis_ref = self.db.collection('analyses').document(playlist_id)
            analysis_doc = analysis_ref.get()
            if analysis_doc.exists:
                analysis_ref.delete()
            
            logger.info(f"Deleted playlist {playlist_id} and all associated data")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting playlist: {e}")
            return False
    
    def get_playlist_summary(self, playlist_id: str) -> Optional[Dict]:
        """Get a summary of playlist data without videos.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Playlist summary if found, None otherwise
        """
        if not self.is_connected():
            return None
        
        try:
            doc_ref = self.db.collection('playlists').document(playlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            playlist_data = doc.to_dict()
            
            # Return summary without videos
            summary = {
                'playlist_id': playlist_data['playlist_id'],
                'title': playlist_data['title'],
                'description': playlist_data['description'],
                'thumbnail_url': playlist_data['thumbnail_url'],
                'channel_title': playlist_data['channel_title'],
                'video_count': playlist_data['video_count'],
                'url': playlist_data['url'],
                'created_at': playlist_data['created_at'],
                'updated_at': playlist_data['updated_at']
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting playlist summary: {e}")
            return None
