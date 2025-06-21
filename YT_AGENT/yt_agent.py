"""
YouTube Playlist Learning Course Generator Agent

A standalone agent that converts YouTube playlists into comprehensive course structures
using Google's Gemini AI and YouTube Data API.
"""

import os
import sys
import json
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
from urllib.parse import urlparse, parse_qs

import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import transcript API with fallback
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    logger.warning("youtube-transcript-api not available. Transcripts will be empty.")


class YouTubeExtractor:
    """Handles YouTube API operations and data extraction."""
    
    def __init__(self, api_key: str):
        """Initialize YouTube API client."""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL."""
        parsed_url = urlparse(url)
        if 'list' in parsed_url.query:
            return parse_qs(parsed_url.query)['list'][0]
        return None
    
    def get_playlist_info(self, playlist_id: str) -> Dict:
        """Get playlist metadata."""
        try:
            response = self.youtube.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            ).execute()
            
            if not response['items']:
                raise ValueError(f"Playlist {playlist_id} not found")
            
            item = response['items'][0]
            snippet = item['snippet']
            
            return {
                'playlist_id': playlist_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'published_at': snippet.get('publishedAt', ''),
                'video_count': item['contentDetails'].get('itemCount', 0)
            }
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """Get all videos from a playlist."""
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
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'transcript': self._get_video_transcript(video_id)                    }
                    
                    videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos
        except HttpError as e:
            logger.error(f"YouTube API error getting videos: {e}")
            raise
    
    def _get_video_details(self, video_id: str) -> Dict:
        """Get additional video details."""
        try:
            response = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=video_id
            ).execute()
            
            if response['items']:
                item = response['items'][0]
                return {
                    'duration': item['contentDetails'].get('duration', ''),
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0))
                }
        except Exception as e:
            logger.warning(f"Could not get video details for {video_id}: {e}")
        
        return {}
    
    def _get_video_transcript(self, video_id: str) -> str:
        """Get video transcript if available."""
        if not TRANSCRIPT_AVAILABLE:
            return ""
        
        try:
            # Try to get transcript in English first, then any available language
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                # Try English first
                transcript = transcript_list.find_transcript(['en'])
            except:
                # Fall back to first available transcript
                transcript = transcript_list.find_generated_transcript(['en'])
            
            # Get the actual transcript data
            transcript_data = transcript.fetch()
            
            # Combine all text segments
            full_transcript = " ".join([entry['text'] for entry in transcript_data])
            
            # Limit transcript length to avoid overwhelming the AI
            if len(full_transcript) > 2000:
                full_transcript = full_transcript[:2000] + "..."
            
            return full_transcript
            
        except Exception as e:
            logger.debug(f"Could not get transcript for video {video_id}: {e}")
            return ""
    
    def extract_playlist_data(self, playlist_url: str, max_videos: int = 50) -> Dict:
        """Extract complete playlist data."""
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            raise ValueError("Invalid YouTube playlist URL")
        
        logger.info(f"Extracting playlist data for: {playlist_id}")
        
        playlist_info = self.get_playlist_info(playlist_id)
        videos = self.get_playlist_videos(playlist_id, max_videos)
        
        return {
            'playlist_info': playlist_info,
            'videos': videos,
            'extracted_at': datetime.now().isoformat()
        }


class CourseGenerator:
    """Generates comprehensive course structures using Google Gemini."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """Initialize Gemini client."""
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        
        # Configure generation settings
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            max_output_tokens=4096,
        )
    
    def generate_comprehensive_course(self, playlist_data: Dict) -> Dict:
        """Generate complete course structure from playlist data."""
        logger.info("Generating comprehensive course structure...")
        
        # Prepare content summary for analysis
        content_summary = self._prepare_content_summary(playlist_data)
        
        # Generate course metadata
        course_info = self._generate_course_info(playlist_data, content_summary)
        
        # Generate modules with lessons
        modules = self._generate_modules(playlist_data, content_summary, course_info)
        
        # Generate assignments
        assignments = self._generate_assignments(modules, course_info)
        
        # Generate final exam
        final_exam = self._generate_final_exam(course_info, modules)
        
        # Create complete course structure
        course_structure = {
            "course": course_info,
            "modules": modules,
            "assignments": assignments,
            "finalExam": final_exam,
            "generatedAt": datetime.now().isoformat(),
            "agentVersion": "2.0",
            "confidence": 0.92,
            "suggestedImprovements": self._generate_improvements(course_info, modules)
        }
        
        logger.info(f"Generated course with {len(modules)} modules")
        return course_structure
    
    def _prepare_content_summary(self, playlist_data: Dict) -> str:
        """Prepare content summary from playlist data."""
        summary_parts = []
        
        # Add playlist info
        playlist_info = playlist_data.get('playlist_info', {})
        summary_parts.append(f"Playlist: {playlist_info.get('title', 'Unknown')}")
        summary_parts.append(f"Channel: {playlist_info.get('channel_title', 'Unknown')}")
        summary_parts.append(f"Description: {playlist_info.get('description', '')[:500]}")
        summary_parts.append("")
        
        # Add video summaries
        for i, video in enumerate(playlist_data.get('videos', [])[:10]):
            summary_parts.append(f"Video {i+1}: {video.get('title', 'Unknown')}")
            summary_parts.append(f"Description: {video.get('description', '')[:200]}")
            if video.get('transcript'):
                transcript_preview = video['transcript'][:300] + "..." if len(video['transcript']) > 300 else video['transcript']
                summary_parts.append(f"Transcript preview: {transcript_preview}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _generate_course_info(self, playlist_data: Dict, content_summary: str) -> Dict:
        """Generate comprehensive course information."""
        playlist_info = playlist_data.get('playlist_info', {})
        
        prompt = f"""
        Based on this YouTube playlist content, generate comprehensive course information:

        {content_summary}

        Generate a JSON object with the following structure:
        {{
            "title": "Course title (clear and descriptive)",
            "description": "Detailed course description (2-3 sentences)",
            "category": "Course category (Programming, Business, Design, etc.)",
            "level": "Difficulty level (Beginner, Intermediate, Advanced)",
            "price": "Suggested price in USD (numeric value)",
            "duration": "Course duration (e.g., '8 weeks')",
            "instructor": "Course instructor name or 'AI Course Generator'",
            "tags": ["array", "of", "relevant", "tags"],
            "thumbnail": "Playlist thumbnail URL or placeholder",
            "prerequisites": ["List of prerequisites"],
            "learningObjectives": ["List of 4-6 learning objectives"],
            "isPublished": true,
            "estimatedHours": "Total estimated hours (numeric)"
        }}        Make it professional and comprehensive. Return ONLY the JSON object.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text.strip()
            parsed_json = self._parse_json_from_response(content)
            if parsed_json:
                course_info = parsed_json
                
                # Ensure thumbnail URL
                if not course_info.get('thumbnail') or course_info['thumbnail'] == 'placeholder':
                    course_info['thumbnail'] = playlist_info.get('thumbnail_url', 'https://via.placeholder.com/640x360?text=Course+Thumbnail')
                
                return course_info
            
        except Exception as e:
            logger.error(f"Error generating course info: {e}")
        
        # Fallback course info
        return {
            "title": playlist_info.get('title', 'Learning Course'),
            "description": "A comprehensive course based on curated YouTube content",
            "category": "Education",
            "level": "Intermediate",
            "price": 99.99,
            "duration": "6 weeks",
            "instructor": "AI Course Generator",
            "tags": ["education", "online-learning", "video-course"],
            "thumbnail": playlist_info.get('thumbnail_url', 'https://via.placeholder.com/640x360?text=Course+Thumbnail'),
            "prerequisites": ["Basic understanding of the subject matter"],
            "learningObjectives": [
                "Understand the core concepts presented in the course",
                "Apply learned knowledge to practical situations",
                "Develop skills through hands-on practice"
            ],
            "isPublished": True,
            "estimatedHours": len(playlist_data.get('videos', [])) * 0.5
        }
    
    def _generate_modules(self, playlist_data: Dict, content_summary: str, course_info: Dict) -> List[Dict]:
        """Generate course modules with lessons."""
        videos = playlist_data.get('videos', [])
        total_videos = len(videos)
        
        # Determine number of modules (aim for 3-6 modules)
        num_modules = max(3, min(6, total_videos // 3))
        videos_per_module = total_videos // num_modules
        
        modules = []
        
        for module_idx in range(num_modules):
            start_idx = module_idx * videos_per_module
            end_idx = start_idx + videos_per_module if module_idx < num_modules - 1 else total_videos
            module_videos = videos[start_idx:end_idx]
            
            module = self._generate_single_module(
                module_idx + 1, 
                module_videos, 
                course_info,
                content_summary
            )
            modules.append(module)
        
        return modules
    
    def _generate_single_module(self, module_number: int, videos: List[Dict], course_info: Dict, content_summary: str) -> Dict:
        """Generate a single module with lessons."""
        # Prepare video summaries for this module
        video_summaries = []
        for video in videos:
            video_summaries.append({
                'title': video.get('title', ''),
                'description': video.get('description', '')[:200],
                'url': video.get('url', ''),
                'video_id': video.get('video_id', ''),
                'duration': video.get('duration', ''),
                'transcript_preview': video.get('transcript', '')[:300] if video.get('transcript') else None
            })
        
        prompt = f"""
        Generate a comprehensive learning module for this course:
        Course: {course_info['title']}
        Module Number: {module_number}
        
        Videos in this module:
        {json.dumps(video_summaries, indent=2)}
        
        Create a JSON object with this structure:
        {{
            "id": "module-{module_number}",
            "title": "Module title",
            "description": "Module description",
            "duration": "Estimated duration (e.g., '2 weeks')",
            "order": {module_number},
            "lessons": [
                {{
                    "id": "lesson-{module_number}-1",
                    "title": "Lesson title",
                    "description": "Lesson description",
                    "type": "video", // video, text, quiz, or project
                    "duration": "Duration in minutes",
                    "order": 1,
                    "content": {{
                        // For video lessons:
                        "videoUrl": "YouTube URL",
                        "videoId": "YouTube video ID",
                        "videoSource": "youtube"
                        
                        // For text lessons:
                        "textContent": "Brief text content",
                        "markdownContent": "Detailed markdown content"
                        
                        // For quiz lessons:
                        "questions": [array of question objects]
                        
                        // For project lessons:
                        "projectDescription": "Project description",
                        "deliverables": ["list of deliverables"],
                        "resources": ["list of resources"]
                    }},
                    "resources": [
                        {{
                            "title": "Resource title",
                            "type": "pdf|link|code",
                            "url": "Resource URL",
                            "description": "Resource description"
                        }}
                    ]
                }}
            ]
        }}
          Make lessons engaging and educational. Include at least one quiz per module.
        Return ONLY the JSON object.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                module_data = json.loads(json_match.group())
                
                # Ensure video lessons use actual video data
                video_copy = videos.copy()
                for lesson in module_data.get('lessons', []):
                    if lesson.get('type') == 'video' and video_copy:
                        video = video_copy.pop(0)
                        lesson['content'] = {
                            'videoUrl': video.get('url', ''),
                            'videoId': video.get('video_id', ''),
                            'videoSource': 'youtube'
                        }
                
                return module_data
            
        except Exception as e:
            logger.error(f"Error generating module {module_number}: {e}")
        
        # Fallback module
        lessons = []
        for i, video in enumerate(videos[:3]):
            lessons.append({
                "id": f"lesson-{module_number}-{i+1}",
                "title": video.get('title', f'Lesson {i+1}'),
                "description": video.get('description', '')[:100] or "Video lesson",
                "type": "video",
                "duration": "20 minutes",
                "order": i + 1,
                "content": {
                    "videoUrl": video.get('url', ''),
                    "videoId": video.get('video_id', ''),
                    "videoSource": "youtube"
                },
                "resources": []
            })
        
        # Add a quiz lesson
        lessons.append({
            "id": f"lesson-{module_number}-quiz",
            "title": f"Module {module_number} Knowledge Check",
            "description": "Test your understanding",
            "type": "quiz",
            "duration": "10 minutes",
            "order": len(lessons) + 1,
            "content": {
                "questions": [
                    {
                        "id": f"q{module_number}-1",
                        "question": "What is the main topic covered in this module?",
                        "type": "multiple-choice",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correctAnswer": 0,
                        "explanation": "Review the module content for the answer."
                    }
                ]
            }
        })
        
        return {
            "id": f"module-{module_number}",
            "title": f"Module {module_number}",
            "description": "Learning module based on video content",
            "duration": "1 week",
            "order": module_number,
            "lessons": lessons
        }
    
    def _generate_assignments(self, modules: List[Dict], course_info: Dict) -> List[Dict]:
        """Generate course assignments."""
        assignments = []
        
        for i, module in enumerate(modules[:3]):
            assignment_id = f"assignment-{i+1}"
            
            prompt = f"""
            Generate an assignment for this course module:
            Course: {course_info['title']}
            Module: {module['title']} - {module['description']}
            
            Create a JSON object:
            {{
                "id": "{assignment_id}",
                "title": "Assignment title",
                "description": "Detailed assignment description (2-3 sentences)",
                "moduleId": "{module['id']}",
                "dueDate": "Due date (ISO format, 2 weeks from now)",
                "points": "Point value (50-150)",
                "submissionType": "file"
            }}
            
            Make it practical and relevant to the module content.
            Return ONLY the JSON object.
            """
            
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                content = response.text.strip()
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    assignment = json.loads(json_match.group())
                    due_date = (datetime.now() + timedelta(weeks=2*(i+1))).isoformat()
                    assignment['dueDate'] = due_date
                    assignments.append(assignment)
                    continue
                    
            except Exception as e:
                logger.error(f"Error generating assignment {i+1}: {e}")
            
            # Fallback assignment
            assignments.append({
                "id": assignment_id,
                "title": f"Module {i+1} Assignment",
                "description": f"Complete practical exercises based on {module['title']} content.",
                "moduleId": module['id'],
                "dueDate": (datetime.now() + timedelta(weeks=2*(i+1))).isoformat(),
                "points": 100,
                "submissionType": "file"
            })
        
        return assignments
    
    def _generate_final_exam(self, course_info: Dict, modules: List[Dict]) -> Dict:
        """Generate final exam."""
        prompt = f"""
        Generate a comprehensive final exam for this course:
        Course: {course_info['title']}
        Description: {course_info['description']}
        
        Modules covered:
        {json.dumps([{"title": m["title"], "description": m["description"]} for m in modules], indent=2)}
        
        Create a JSON object:
        {{
            "title": "Final exam title",
            "description": "Exam description",
            "timeLimit": "Time limit in minutes (90-180)",
            "passingScore": "Passing score percentage (70-80)",
            "questions": [
                {{
                    "id": "final-q1",
                    "question": "Essay question text",
                    "type": "essay",
                    "points": "Point value (10-20)"
                }},
                {{
                    "id": "final-q2",
                    "question": "Multiple choice question",
                    "type": "multiple-choice",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correctAnswer": 0,
                    "points": "Point value (5-10)"
                }}
            ]
        }}
        
        Include 3-5 questions mixing essay and multiple choice.
        Return ONLY the JSON object.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            logger.error(f"Error generating final exam: {e}")
        
        # Fallback final exam
        return {
            "title": f"{course_info['title']} Final Exam",
            "description": "Comprehensive exam covering all course topics and modules.",
            "timeLimit": 120,
            "passingScore": 75,
            "questions": [
                {
                    "id": "final-q1",
                    "question": f"Explain the key concepts covered in {course_info['title']} and how they relate to each other.",
                    "type": "essay",
                    "points": 20
                },
                {
                    "id": "final-q2",
                    "question": "Which of the following best describes the main focus of this course?",
                    "type": "multiple-choice",
                    "options": [
                        "Theoretical foundations",
                        "Practical applications",
                        "Historical context",
                        "Future trends"
                    ],
                    "correctAnswer": 1,
                    "points": 10
                }
            ]
        }
    
    def _generate_improvements(self, course_info: Dict, modules: List[Dict]) -> List[str]:
        """Generate suggested improvements for the course."""
        return [
            "Consider adding more hands-on exercises and practical projects",
            "Include additional real-world case studies and examples",
            "Add supplementary reading materials and external resources",
            "Consider creating discussion forums for student interaction",
            "Add video transcripts and accessibility features"
        ]
    
    def _parse_json_from_response(self, content: str) -> Optional[Dict]:
        """Safely parse JSON from AI response with multiple fallback strategies."""
        if not content:
            return None
        
        content = content.strip()
        
        # Strategy 1: Try direct JSON parse if content looks like JSON
        if content.startswith('{') and content.endswith('}'):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Find JSON block using regex
        patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON code block
            r'```\s*(\{.*?\})\s*```',      # Generic code block
            r'(\{.*?\})',                   # Any JSON object
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match.strip())
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # Strategy 3: Try to fix common JSON issues
        try:
            # Remove common markdown formatting
            cleaned = re.sub(r'```json|```', '', content)
            cleaned = cleaned.strip()
            
            # Try parsing again
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        logger.warning(f"Could not parse JSON from AI response: {content[:200]}...")
        return None


class YouTubeAgent:
    """Main agent class that orchestrates the course generation process."""
    
    def __init__(self, youtube_api_key: str, gemini_api_key: str, output_dir: str = "output"):
        """Initialize the YouTube agent."""
        self.extractor = YouTubeExtractor(youtube_api_key)
        self.generator = CourseGenerator(gemini_api_key)
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def process_playlist(self, playlist_url: str, max_videos: int = 20) -> str:
        """Process a YouTube playlist and generate a comprehensive course."""
        try:
            logger.info(f"Starting course generation for: {playlist_url}")
            
            # Step 1: Extract playlist data
            logger.info("Step 1: Extracting playlist data...")
            playlist_data = self.extractor.extract_playlist_data(playlist_url, max_videos)
            
            # Step 2: Generate comprehensive course
            logger.info("Step 2: Generating comprehensive course structure...")
            course_structure = self.generator.generate_comprehensive_course(playlist_data)
            
            # Step 3: Save to output file
            logger.info("Step 3: Saving course structure...")
            output_file = self._save_course(course_structure, playlist_data)
            
            logger.info(f"Course generation completed successfully!")
            logger.info(f"Output saved to: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing playlist: {e}")
            raise
    
    def _save_course(self, course_structure: Dict, playlist_data: Dict) -> str:
        """Save course structure to JSON file."""
        # Generate filename from course title
        course_title = course_structure.get('course', {}).get('title', 'Course')
        safe_title = re.sub(r'[^\w\s-]', '', course_title).strip().replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_title}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Add metadata
        output_data = {
            **course_structure,
            "metadata": {
                "source_playlist": playlist_data.get('playlist_info', {}),
                "total_videos_processed": len(playlist_data.get('videos', [])),
                "extraction_timestamp": playlist_data.get('extracted_at'),
                "agent_info": {
                    "name": "YouTube Course Generator Agent",
                    "version": "1.0.0",
                    "created_by": "AI Assistant"
                }
            }
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_course_summary(self, course_structure: Dict) -> str:
        """Generate a summary of the created course."""
        course = course_structure.get('course', {})
        modules = course_structure.get('modules', [])
        assignments = course_structure.get('assignments', [])
        final_exam = course_structure.get('finalExam', {})
        
        summary = f"""
Course Generation Summary
========================

📚 Course: {course.get('title', 'N/A')}
🏷️  Category: {course.get('category', 'N/A')}
📈 Level: {course.get('level', 'N/A')}
💰 Price: ${course.get('price', 0)}
⏱️  Duration: {course.get('duration', 'N/A')}
👨‍🏫 Instructor: {course.get('instructor', 'N/A')}
🕐 Estimated Hours: {course.get('estimatedHours', 0)}

📖 Structure:
- Modules: {len(modules)}
- Lessons: {sum(len(m.get('lessons', [])) for m in modules)}
- Assignments: {len(assignments)}
- Final Exam: {'Yes' if final_exam else 'No'}

🎯 Learning Objectives:
"""
        for i, obj in enumerate(course.get('learningObjectives', []), 1):
            summary += f"   {i}. {obj}\n"
        
        summary += "\n📖 Modules Overview:\n"
        for i, module in enumerate(modules, 1):
            lessons = module.get('lessons', [])
            summary += f"   Module {i}: {module.get('title', 'N/A')} ({len(lessons)} lessons)\n"
        
        return summary


def main():
    """Main function to run the YouTube agent."""
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    gemini_api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not youtube_api_key or not gemini_api_key:
        print("❌ Error: Missing required API keys")
        print("Please set the following environment variables:")
        print("  - YOUTUBE_API_KEY")
        print("  - GOOGLE_AI_API_KEY")
        return
    
    # Initialize agent
    agent = YouTubeAgent(youtube_api_key, gemini_api_key, "output")
    
    # Get playlist URL from user
    if len(sys.argv) > 1:
        playlist_url = sys.argv[1]
    else:
        playlist_url = input("Enter YouTube playlist URL: ").strip()
    
    if not playlist_url:
        print("❌ Error: Playlist URL is required")
        return
    
    # Get max videos (optional)
    max_videos = 20
    if len(sys.argv) > 2:
        try:
            max_videos = int(sys.argv[2])
        except ValueError:
            print("⚠️  Warning: Invalid max videos number, using default (20)")
    
    try:
        print("🚀 YouTube Course Generator Agent Starting...")
        print(f"📥 Processing playlist: {playlist_url}")
        print(f"📊 Max videos: {max_videos}")
        print("-" * 60)
        
        # Process playlist
        output_file = agent.process_playlist(playlist_url, max_videos)
        
        # Load and display summary
        with open(output_file, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        print(agent.get_course_summary(course_data))
        print(f"💾 Course saved to: {output_file}")
        print("✅ Course generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
