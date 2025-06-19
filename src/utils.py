"""Utility Functions

Common utility functions used across the application.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_youtube_url(url: str) -> bool:
    """Validate if a URL is a valid YouTube playlist URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube playlist URL, False otherwise
    """
    try:
        parsed = urlparse(url)
        
        # Check if it's a YouTube domain
        if 'youtube.com' not in parsed.netloc and 'youtu.be' not in parsed.netloc:
            return False
        
        # Check if it contains a playlist parameter
        if 'list=' in url:
            return True
        
        return False
    except Exception:
        return False


def clean_text(text: str) -> str:
    """Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.,!?;:()\[\]{}\"\'`]', '', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add ellipsis
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    if add_ellipsis:
        truncated += "..."
    
    return truncated


def format_time_duration(seconds: int) -> str:
    """Format seconds into human-readable duration.
    
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
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_seconds = seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        
        time_str = f"{hours}h"
        if minutes > 0:
            time_str += f" {minutes}m"
        if seconds > 0:
            time_str += f" {seconds}s"
        
        return time_str


def safe_get_nested(data: Dict, keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary values.
    
    Args:
        data: Dictionary to search
        keys: List of keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
    """
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default


def ensure_directory(directory: str) -> None:
    """Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path to ensure
    """
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Could not create directory {directory}: {e}")
        raise


def save_json(data: Dict, filepath: str, indent: int = 2) -> None:
    """Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
    """
    try:
        ensure_directory(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Could not save JSON to {filepath}: {e}")
        raise


def load_json(filepath: str) -> Optional[Dict]:
    """Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load JSON from {filepath}: {e}")
        return None


def extract_video_id_from_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time for text.
    
    Args:
        text: Text to analyze
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, word_count // words_per_minute)
    
    return reading_time


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra spaces and dots
    filename = re.sub(r'\.+', '.', filename)
    filename = re.sub(r'\s+', ' ', filename)
    
    # Limit length
    filename = filename[:200]
    
    return filename.strip()


def create_slug(text: str) -> str:
    """Create URL-friendly slug from text.
    
    Args:
        text: Text to convert
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def estimate_complexity_score(text: str) -> float:
    """Estimate complexity score of text content.
    
    Args:
        text: Text to analyze
        
    Returns:
        Complexity score (0.0 to 1.0)
    """
    if not text:
        return 0.0
    
    # Simple heuristics for complexity
    sentences = text.split('.')
    words = text.split()
    
    if not sentences or not words:
        return 0.0
    
    # Average sentence length
    avg_sentence_length = len(words) / len(sentences)
    
    # Count complex words (>6 characters)
    complex_words = sum(1 for word in words if len(word) > 6)
    complex_ratio = complex_words / len(words)
    
    # Count technical terms (rough approximation)
    technical_indicators = ['algorithm', 'analysis', 'implementation', 'architecture', 'methodology']
    technical_score = sum(1 for indicator in technical_indicators if indicator in text.lower())
    
    # Combine factors
    complexity = min(1.0, (avg_sentence_length / 20) * 0.4 + complex_ratio * 0.4 + (technical_score / 10) * 0.2)
    
    return complexity


def group_by_similarity(items: List[Dict], key: str, threshold: float = 0.7) -> List[List[Dict]]:
    """Group items by similarity of a specific key.
    
    Args:
        items: List of dictionaries to group
        key: Key to compare for similarity
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        List of groups (each group is a list of similar items)
    """
    if not items:
        return []
    
    groups = []
    
    for item in items:
        item_value = item.get(key, '')
        if not item_value:
            continue
        
        # Find existing group or create new one
        placed = False
        for group in groups:
            # Simple similarity check (can be improved with more sophisticated algorithms)
            for group_item in group:
                group_value = group_item.get(key, '')
                if _simple_similarity(item_value, group_value) >= threshold:
                    group.append(item)
                    placed = True
                    break
            if placed:
                break
        
        if not placed:
            groups.append([item])
    
    return groups


def _simple_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    if not text1 or not text2:
        return 0.0
    
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the process
        """
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, increment: int = 1) -> None:
        """Update progress.
        
        Args:
            increment: Number of items completed
        """
        self.current = min(self.current + increment, self.total)
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def is_complete(self) -> bool:
        """Check if processing is complete.
        
        Returns:
            True if complete, False otherwise
        """
        return self.current >= self.total
