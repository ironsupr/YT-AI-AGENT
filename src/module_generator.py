"""Learning Module Generator

This module creates structured learning modules from analyzed content,
generating student-friendly materials with clear organization and progression.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import markdown

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModuleGenerator:
    """Generates structured learning modules from analyzed content."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize module generator.
        
        Args:
            output_dir: Directory to save generated modules
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_learning_modules(self, analysis_results: Dict) -> Dict:
        """Generate complete learning modules from analysis results.
        
        Args:
            analysis_results: Results from ContentAnalyzer
            
        Returns:
            Generated modules data
        """
        logger.info("Generating learning modules...")
        
        # Create main course structure
        course_data = self._create_course_structure(analysis_results)
        
        # Generate individual modules
        modules = []
        for path_module in analysis_results.get('learning_path', []):
            module = self._create_module(path_module, analysis_results)
            modules.append(module)
        
        # Generate additional materials
        study_guide = self._generate_study_guide(analysis_results)
        quiz_questions = self._generate_quiz_questions(analysis_results)
        progress_tracker = self._create_progress_tracker(modules)
        
        # Create final course package
        course_package = {
            'course_info': course_data,
            'modules': modules,
            'study_guide': study_guide,
            'quiz_questions': quiz_questions,
            'progress_tracker': progress_tracker,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save to files
        self._save_course_package(course_package)
        
        logger.info(f"Generated {len(modules)} learning modules")
        return course_package
    
    def _create_course_structure(self, analysis_results: Dict) -> Dict:
        """Create main course structure and metadata.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Course structure data
        """
        return {
            'title': analysis_results.get('playlist_title', 'Learning Course'),
            'description': self._generate_course_description(analysis_results),
            'learning_objectives': analysis_results.get('learning_objectives', []),
            'prerequisites': analysis_results.get('prerequisites', []),
            'difficulty_level': analysis_results.get('difficulty_level', 'intermediate'),
            'estimated_time': analysis_results.get('estimated_completion_time', 'Unknown'),
            'total_modules': len(analysis_results.get('learning_path', [])),
            'total_videos': len(analysis_results.get('video_analyses', [])),
            'subject': analysis_results.get('structure_analysis', {}).get('subject', 'General'),
            'approach': analysis_results.get('structure_analysis', {}).get('approach', 'mixed')
        }
    
    def _create_module(self, path_module: Dict, analysis_results: Dict) -> Dict:
        """Create a single learning module.
        
        Args:
            path_module: Module from learning path
            analysis_results: Full analysis results
            
        Returns:
            Complete module data
        """
        module_videos = path_module.get('videos', [])
        
        module = {
            'module_id': f"module_{path_module.get('order', 1)}",
            'title': path_module.get('module_name', 'Learning Module'),
            'description': path_module.get('description', ''),
            'order': path_module.get('order', 1),
            'learning_objectives': self._extract_module_objectives(module_videos),
            'videos': self._format_module_videos(module_videos),
            'key_concepts': self._extract_key_concepts(module_videos),
            'summary': self._generate_module_summary(module_videos),
            'estimated_time': self._calculate_module_time(module_videos),
            'difficulty': self._assess_module_difficulty(module_videos),
            'activities': self._suggest_learning_activities(module_videos),
            'resources': self._compile_additional_resources(module_videos)
        }
        
        return module
    
    def _generate_course_description(self, analysis_results: Dict) -> str:
        """Generate a comprehensive course description.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Course description
        """
        structure = analysis_results.get('structure_analysis', {})
        subject = structure.get('subject', 'Educational Content')
        themes = structure.get('themes', [])
        
        description = f"This course covers {subject.lower()}"
        
        if themes:
            description += f", focusing on {', '.join(themes[:3])}"
        
        description += f". The course is designed for {structure.get('audience_level', 'intermediate')} learners"
        description += f" and follows a {structure.get('approach', 'mixed')} approach."
        
        return description
    
    def _extract_module_objectives(self, videos: List[Dict]) -> List[str]:
        """Extract learning objectives for a module.
        
        Args:
            videos: Videos in the module
            
        Returns:
            List of module objectives
        """
        objectives = []
        
        for video in videos:
            video_objectives = video.get('learning_outcomes', [])
            for objective in video_objectives:
                if objective not in objectives:
                    objectives.append(objective)
        
        # Limit to 5 most important objectives
        return objectives[:5]
    
    def _format_module_videos(self, videos: List[Dict]) -> List[Dict]:
        """Format videos for module display.
        
        Args:
            videos: Raw video data
            
        Returns:
            Formatted video data
        """
        formatted_videos = []
        
        for video in videos:
            formatted_video = {
                'id': video.get('video_id', ''),
                'title': video.get('title', ''),
                'summary': video.get('summary', ''),
                'key_concepts': video.get('key_concepts', []),
                'difficulty': video.get('difficulty', 'unknown'),
                'url': f"https://www.youtube.com/watch?v={video.get('video_id', '')}",
                'notes_section': self._create_notes_template(video),
                'reflection_questions': self._generate_reflection_questions(video)
            }
            formatted_videos.append(formatted_video)
        
        return formatted_videos
    
    def _extract_key_concepts(self, videos: List[Dict]) -> List[str]:
        """Extract all key concepts from module videos.
        
        Args:
            videos: Videos in the module
            
        Returns:
            List of unique key concepts
        """
        concepts = []
        
        for video in videos:
            video_concepts = video.get('key_concepts', [])
            for concept in video_concepts:
                if concept not in concepts:
                    concepts.append(concept)
        
        return concepts
    
    def _generate_module_summary(self, videos: List[Dict]) -> str:
        """Generate a summary for the module.
        
        Args:
            videos: Videos in the module
            
        Returns:
            Module summary
        """
        if not videos:
            return "This module contains educational content."
        
        # Combine video summaries
        summaries = [v.get('summary', '') for v in videos if v.get('summary')]
        
        if summaries:
            return f"This module covers: {' '.join(summaries[:2])}"
        else:
            return f"This module contains {len(videos)} educational videos."
    
    def _calculate_module_time(self, videos: List[Dict]) -> str:
        """Calculate estimated time for module completion.
        
        Args:
            videos: Videos in the module
            
        Returns:
            Estimated time string
        """
        # Estimate 10 minutes per video for watching + study time
        estimated_minutes = len(videos) * 10
        
        if estimated_minutes < 60:
            return f"{estimated_minutes} minutes"
        else:
            hours = estimated_minutes // 60
            minutes = estimated_minutes % 60
            return f"{hours}h {minutes}m"
    
    def _assess_module_difficulty(self, videos: List[Dict]) -> str:
        """Assess overall difficulty of the module.
        
        Args:
            videos: Videos in the module
            
        Returns:
            Difficulty level
        """
        difficulties = [v.get('difficulty', 'intermediate') for v in videos]
        
        if 'advanced' in difficulties:
            return 'advanced'
        elif 'beginner' in difficulties:
            return 'beginner'
        else:
            return 'intermediate'
    
    def _suggest_learning_activities(self, videos: List[Dict]) -> List[Dict]:
        """Suggest learning activities for the module.
        
        Args:
            videos: Videos in the module
            
        Returns:
            List of suggested activities
        """
        activities = [
            {
                'type': 'note_taking',
                'title': 'Take Detailed Notes',
                'description': 'Create comprehensive notes while watching each video',
                'estimated_time': '15 minutes per video'
            },
            {
                'type': 'concept_mapping',
                'title': 'Create Concept Maps',
                'description': 'Draw connections between key concepts covered',
                'estimated_time': '20 minutes'
            },
            {
                'type': 'practice',
                'title': 'Apply Concepts',
                'description': 'Practice applying the concepts learned in real scenarios',
                'estimated_time': '30 minutes'
            },
            {
                'type': 'discussion',
                'title': 'Discuss with Peers',
                'description': 'Discuss key concepts with classmates or study groups',
                'estimated_time': '15 minutes'
            }
        ]
        
        return activities
    
    def _compile_additional_resources(self, videos: List[Dict]) -> List[Dict]:
        """Compile additional learning resources.
        
        Args:
            videos: Videos in the module
            
        Returns:
            List of additional resources
        """
        resources = [
            {
                'type': 'glossary',
                'title': 'Key Terms Glossary',
                'description': 'Definitions of important terms and concepts',
                'url': '#glossary'
            },
            {
                'type': 'references',
                'title': 'Further Reading',
                'description': 'Additional resources for deeper learning',
                'url': '#references'
            },
            {
                'type': 'practice',
                'title': 'Practice Exercises',
                'description': 'Hands-on exercises to reinforce learning',
                'url': '#exercises'
            }
        ]
        
        return resources
    
    def _create_notes_template(self, video: Dict) -> Dict:
        """Create a notes template for a video.
        
        Args:
            video: Video data
            
        Returns:
            Notes template structure
        """
        return {
            'title': f"Notes for: {video.get('title', 'Video')}",
            'sections': [
                {
                    'name': 'Key Points',
                    'template': '• Point 1:\n• Point 2:\n• Point 3:'
                },
                {
                    'name': 'Questions',
                    'template': '• Question 1:\n• Question 2:'
                },
                {
                    'name': 'Personal Insights',
                    'template': 'What did I learn?\n\nHow can I apply this?'
                }
            ]
        }
    
    def _generate_reflection_questions(self, video: Dict) -> List[str]:
        """Generate reflection questions for a video.
        
        Args:
            video: Video data
            
        Returns:
            List of reflection questions
        """
        general_questions = [
            "What are the main concepts covered in this video?",
            "How do these concepts relate to what I already know?",
            "What questions do I still have about this topic?",
            "How can I apply this knowledge in practice?"
        ]
        
        # Add specific questions based on video content
        key_concepts = video.get('key_concepts', [])
        if key_concepts:
            specific_questions = [
                f"How would you explain {concept} to someone else?" for concept in key_concepts[:2]
            ]
            return general_questions + specific_questions
        
        return general_questions
    
    def _generate_study_guide(self, analysis_results: Dict) -> Dict:
        """Generate a comprehensive study guide.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Study guide data
        """
        return {
            'title': f"Study Guide: {analysis_results.get('playlist_title', 'Course')}",
            'overview': analysis_results.get('content_summary', '')[:500] + "...",
            'learning_objectives': analysis_results.get('learning_objectives', []),
            'key_concepts': self._compile_all_concepts(analysis_results),
            'study_tips': [
                "Watch each video actively, taking notes on key concepts",
                "Pause frequently to reflect on what you've learned",
                "Create your own examples to illustrate concepts",
                "Review notes regularly to reinforce learning",
                "Connect new concepts to previous knowledge"
            ],
            'study_schedule': self._create_study_schedule(analysis_results)
        }
    
    def _generate_quiz_questions(self, analysis_results: Dict) -> List[Dict]:
        """Generate quiz questions based on content.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            List of quiz questions
        """
        questions = []
        
        # Generate questions from key concepts
        all_concepts = self._compile_all_concepts(analysis_results)
        
        for concept in all_concepts[:10]:  # Limit to 10 questions
            questions.append({
                'question': f"Explain the concept of {concept} and its significance.",
                'type': 'short_answer',
                'topic': concept,
                'difficulty': 'intermediate'
            })
        
        # Add some multiple choice questions
        objectives = analysis_results.get('learning_objectives', [])
        for objective in objectives[:5]:
            questions.append({
                'question': f"Which of the following best describes: {objective}?",
                'type': 'multiple_choice',
                'options': ['A', 'B', 'C', 'D'],
                'topic': 'learning_objectives',
                'difficulty': 'intermediate'
            })
        
        return questions
    
    def _create_progress_tracker(self, modules: List[Dict]) -> Dict:
        """Create a progress tracking structure.
        
        Args:
            modules: Generated modules
            
        Returns:
            Progress tracker data
        """
        return {
            'total_modules': len(modules),
            'modules_completed': 0,
            'completion_percentage': 0,
            'module_progress': [
                {
                    'module_id': module['module_id'],
                    'title': module['title'],
                    'completed': False,
                    'videos_watched': 0,
                    'total_videos': len(module['videos']),
                    'notes_taken': False,
                    'activities_completed': 0,
                    'total_activities': len(module['activities'])
                }
                for module in modules
            ],
            'study_streak': 0,
            'last_study_date': None
        }
    
    def _compile_all_concepts(self, analysis_results: Dict) -> List[str]:
        """Compile all key concepts from the analysis.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            List of all unique concepts
        """
        concepts = []
        
        for video in analysis_results.get('video_analyses', []):
            video_concepts = video.get('key_concepts', [])
            for concept in video_concepts:
                if concept not in concepts:
                    concepts.append(concept)
        
        return concepts
    
    def _create_study_schedule(self, analysis_results: Dict) -> List[Dict]:
        """Create a suggested study schedule.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Study schedule data
        """
        modules = analysis_results.get('learning_path', [])
        schedule = []
        
        for i, module in enumerate(modules, 1):
            schedule.append({
                'week': i,
                'module': module.get('module_name', f'Module {i}'),
                'activities': [
                    'Watch all videos in the module',
                    'Take detailed notes',
                    'Complete reflection questions',
                    'Review and summarize key concepts'
                ],
                'estimated_time': '2-3 hours'
            })
        
        return schedule
    
    def _save_course_package(self, course_package: Dict) -> None:
        """Save the complete course package to files.
        
        Args:
            course_package: Complete course data
        """
        # Save JSON data
        json_file = os.path.join(self.output_dir, 'course_data.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(course_package, f, indent=2, ensure_ascii=False)
        
        # Generate HTML version
        html_file = os.path.join(self.output_dir, 'course_guide.html')
        html_content = self._generate_html_course(course_package)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate Markdown version
        md_file = os.path.join(self.output_dir, 'course_guide.md')
        md_content = self._generate_markdown_course(course_package)
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Course package saved to {self.output_dir}")
    
    def _generate_html_course(self, course_package: Dict) -> str:
        """Generate HTML version of the course.
        
        Args:
            course_package: Course data
            
        Returns:
            HTML content
        """
        course_info = course_package['course_info']
        modules = course_package['modules']
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{course_info['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .course-header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .module {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .video {{ margin: 10px 0; padding: 10px; background: #f9f9f9; }}
                .objectives {{ background: #e8f4f8; padding: 10px; margin: 10px 0; }}
                ul {{ padding-left: 20px; }}
            </style>
        </head>
        <body>
            <div class="course-header">
                <h1>{course_info['title']}</h1>
                <p>{course_info['description']}</p>
                <p><strong>Difficulty:</strong> {course_info['difficulty_level']}</p>
                <p><strong>Estimated Time:</strong> {course_info['estimated_time']}</p>
            </div>
            
            <div class="objectives">
                <h2>Learning Objectives</h2>
                <ul>
                    {"".join(f"<li>{obj}</li>" for obj in course_info['learning_objectives'])}
                </ul>
            </div>
        """
        
        for module in modules:
            html += f"""
            <div class="module">
                <h2>Module {module['order']}: {module['title']}</h2>
                <p>{module['description']}</p>
                <p><strong>Estimated Time:</strong> {module['estimated_time']}</p>
                
                <h3>Videos</h3>
                {"".join(f'<div class="video"><h4>{video["title"]}</h4><p>{video["summary"]}</p><a href="{video["url"]}" target="_blank">Watch Video</a></div>' for video in module['videos'])}
                
                <h3>Key Concepts</h3>
                <ul>
                    {"".join(f"<li>{concept}</li>" for concept in module['key_concepts'])}
                </ul>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_course(self, course_package: Dict) -> str:
        """Generate Markdown version of the course.
        
        Args:
            course_package: Course data
            
        Returns:
            Markdown content
        """
        course_info = course_package['course_info']
        modules = course_package['modules']
        
        md = f"""# {course_info['title']}

{course_info['description']}

**Difficulty Level:** {course_info['difficulty_level']}  
**Estimated Time:** {course_info['estimated_time']}  
**Total Modules:** {course_info['total_modules']}

## Learning Objectives

"""
        
        for obj in course_info['learning_objectives']:
            md += f"- {obj}\n"
        
        md += "\n## Prerequisites\n\n"
        for prereq in course_info.get('prerequisites', []):
            md += f"- {prereq}\n"
        
        md += "\n## Course Modules\n\n"
        
        for module in modules:
            md += f"""### Module {module['order']}: {module['title']}

{module['description']}

**Estimated Time:** {module['estimated_time']}  
**Difficulty:** {module['difficulty']}

#### Videos

"""
            
            for video in module['videos']:
                md += f"""##### {video['title']}

{video['summary']}

**Key Concepts:** {', '.join(video['key_concepts'])}

[Watch Video]({video['url']})

"""
            
            md += "#### Learning Activities\n\n"
            for activity in module['activities']:
                md += f"- **{activity['title']}:** {activity['description']} ({activity['estimated_time']})\n"
            
            md += "\n---\n\n"
        
        return md
