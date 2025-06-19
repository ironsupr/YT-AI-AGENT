"""YouTube Data Extraction Module

This module handles all YouTube API interactions to extract playlist information,
video metadata, and transcripts.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeExtractor:
    """Handles YouTube API operations and data extraction."""
    
    def __init__(self, api_key: str):
        """Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.formatter = TextFormatter()
    
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL.
        
        Args:
            url: YouTube playlist URL
            
        Returns:
            Playlist ID if valid, None otherwise
        """
        try:
            parsed = urlparse(url)
            if 'youtube.com' not in parsed.netloc and 'youtu.be' not in parsed.netloc:
                return None
            
            # Handle different URL formats
            if 'list=' in url:
                return parse_qs(parsed.query).get('list', [None])[0]
            
            # Handle shortened URLs
            if 'youtu.be' in parsed.netloc and 'list=' in parsed.query:
                return parse_qs(parsed.query).get('list', [None])[0]
                
            return None
        except Exception as e:
            logger.error(f"Error extracting playlist ID: {e}")
            return None
    
    def get_playlist_info(self, playlist_id: str) -> Dict:
        """Get basic playlist information.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Dictionary containing playlist metadata
        """
        try:
            response = self.youtube.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            ).execute()
            
            if not response['items']:
                raise ValueError(f"Playlist {playlist_id} not found")
            
            playlist = response['items'][0]
            snippet = playlist['snippet']
            
            return {
                'id': playlist_id,
                'title': snippet.get('title', 'Unknown Playlist'),
                'description': snippet.get('description', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'video_count': playlist['contentDetails'].get('itemCount', 0)
            }
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            raise
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """Get all videos from a playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of video dictionaries
        """
        videos = []
        next_page_token = None
        
        try:
            while len(videos) < max_results:
                response = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in response['items']:
                    snippet = item['snippet']
                    video_id = snippet['resourceId']['videoId']
                    
                    # Get additional video details
                    video_details = self._get_video_details(video_id)
                    
                    video_info = {
                        'video_id': video_id,
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'position': snippet.get('position', 0),
                        'duration': video_details.get('duration', ''),
                        'view_count': video_details.get('view_count', 0),
                        'like_count': video_details.get('like_count', 0),
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    }
                    
                    videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos
        except HttpError as e:
            logger.error(f"YouTube API error getting videos: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting playlist videos: {e}")
            raise
    
    def _get_video_details(self, video_id: str) -> Dict:
        """Get additional video details like duration and statistics.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video details
        """
        try:
            response = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not response['items']:
                return {}
            
            video = response['items'][0]
            content_details = video.get('contentDetails', {})
            statistics = video.get('statistics', {})
            
            return {
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0))
            }
        except Exception as e:
            logger.warning(f"Could not get video details for {video_id}: {e}")
            return {}
    
    def get_video_transcript(self, video_id: str, languages: List[str] = ['en']) -> Optional[str]:
        """Get video transcript if available.
        
        Args:
            video_id: YouTube video ID
            languages: List of preferred languages
            
        Returns:
            Transcript text or None if not available
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get transcript in preferred languages
            for language in languages:
                try:
                    transcript = transcript_list.find_transcript([language])
                    transcript_data = transcript.fetch()
                    return self.formatter.format_transcript(transcript_data)
                except Exception:
                    continue
            
            # If no preferred language found, try auto-generated English
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                transcript_data = transcript.fetch()
                return self.formatter.format_transcript(transcript_data)
            except Exception:
                pass
            
            # Try any available transcript
            try:
                transcript = transcript_list.find_transcript(transcript_list._transcript_data.keys())
                transcript_data = transcript.fetch()
                return self.formatter.format_transcript(transcript_data)
            except Exception:
                pass
                
            return None
        except Exception as e:
            logger.warning(f"Could not get transcript for video {video_id}: {e}")
            return None
    
    def extract_playlist_data(self, playlist_url: str, max_videos: int = 50) -> Dict:
        """Complete playlist data extraction.
        
        Args:
            playlist_url: YouTube playlist URL
            max_videos: Maximum number of videos to process
            
        Returns:
            Complete playlist data with videos and transcripts
        """
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            raise ValueError("Invalid YouTube playlist URL")
        
        logger.info(f"Extracting data for playlist: {playlist_id}")
        
        # Get playlist information
        playlist_info = self.get_playlist_info(playlist_id)
        
        # Get videos
        videos = self.get_playlist_videos(playlist_id, max_videos)
        
        # Get transcripts for videos
        for video in videos:
            logger.info(f"Getting transcript for video: {video['title']}")
            transcript = self.get_video_transcript(video['video_id'])
            video['transcript'] = transcript
        
        playlist_data = {
            'playlist_info': playlist_info,
            'videos': videos,
            'total_videos': len(videos),
            'videos_with_transcripts': sum(1 for v in videos if v.get('transcript'))
        }
        
        logger.info(f"Extracted {len(videos)} videos, {playlist_data['videos_with_transcripts']} with transcripts")
        
        return playlist_data


def parse_duration(duration: str) -> int:
    """Parse ISO 8601 duration to seconds.
    
    Args:
        duration: ISO 8601 duration string (e.g., 'PT4M13S')
        
    Returns:
        Duration in seconds
    """
    if not duration:
        return 0
    
    # Remove PT prefix
    duration = duration.replace('PT', '')
    
    # Extract hours, minutes, seconds
    hours = 0
    minutes = 0
    seconds = 0
    
    if 'H' in duration:
        hours = int(duration.split('H')[0])
        duration = duration.split('H')[1]
    
    if 'M' in duration:
        minutes = int(duration.split('M')[0])
        duration = duration.split('M')[1]
    
    if 'S' in duration:
        seconds = int(duration.replace('S', ''))
    
    return hours * 3600 + minutes * 60 + seconds


def format_duration(seconds: int) -> str:
    """Format seconds to human-readable duration.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_seconds = seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return f"{hours}h {minutes}m {seconds}s"
