"""Enhanced AI-Powered Content Analysis Module

This module uses Google's Gemini AI to create comprehensive course structures
with modules, lessons, quizzes, and assignments in the specified JSON format.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime, timedelta
import uuid

import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedContentAnalyzer:
    """Handles comprehensive course generation using Google Gemini."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """Initialize Gemini client.
        
        Args:
            api_key: Google AI API key
            model: Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        
        # Configure generation settings for consistent responses
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            max_output_tokens=4096,
        )
    
    def generate_comprehensive_course(self, playlist_data: Dict) -> Dict:
        """Generate complete course structure from playlist data.
        
        Args:
            playlist_data: Complete playlist data from YouTubeExtractor
            
        Returns:
            Complete course structure in the specified JSON format
        """
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
        for i, video in enumerate(playlist_data.get('videos', [])[:10]):  # Limit for context
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
        }}

        Make it professional and comprehensive. Return ONLY the JSON object.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                course_info = json.loads(json_match.group())
                
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
                // Generate 2-4 lessons per module, mixing video lessons with text/quiz/project lessons
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
                for lesson in module_data.get('lessons', []):
                    if lesson.get('type') == 'video' and videos:
                        # Find matching video or use first available
                        video = videos[0] if videos else None
                        if video:
                            lesson['content'] = {
                                'videoUrl': video.get('url', ''),
                                'videoId': video.get('video_id', ''),
                                'videoSource': 'youtube'
                            }
                            videos.pop(0)  # Remove used video
                
                return module_data
            
        except Exception as e:
            logger.error(f"Error generating module {module_number}: {e}")
        
        # Fallback module
        lessons = []
        for i, video in enumerate(videos[:3]):  # Max 3 lessons per module
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
        
        for i, module in enumerate(modules[:3]):  # Generate assignments for first 3 modules
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
                    # Ensure due date is set
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
