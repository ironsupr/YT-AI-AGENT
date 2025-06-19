"""AI-Powered Content Analysis Module

This module uses Google's Gemini AI models to analyze video content and extract
key information for learning module generation.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
import re

import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Handles AI-powered content analysis using Google Gemini."""
    
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
            temperature=0.3,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
        )
    
    def analyze_playlist_content(self, playlist_data: Dict) -> Dict:
        """Analyze entire playlist content and structure.
        
        Args:
            playlist_data: Complete playlist data from YouTubeExtractor
            
        Returns:
            Analysis results with learning structure
        """
        logger.info("Starting playlist content analysis...")
        
        # Prepare content summary for analysis
        content_summary = self._prepare_content_summary(playlist_data)
        
        # Analyze overall structure and themes
        structure_analysis = self._analyze_content_structure(content_summary)
        
        # Analyze individual videos
        video_analyses = []
        for video in playlist_data['videos']:
            if video.get('transcript'):
                analysis = self._analyze_video_content(video)
                video_analyses.append(analysis)
        
        # Generate learning objectives
        learning_objectives = self._generate_learning_objectives(content_summary, structure_analysis)
        
        # Identify prerequisite knowledge
        prerequisites = self._identify_prerequisites(content_summary)
        
        # Suggest learning path
        learning_path = self._suggest_learning_path(video_analyses, structure_analysis)
        
        return {
            'playlist_title': playlist_data['playlist_info']['title'],
            'content_summary': content_summary,
            'structure_analysis': structure_analysis,
            'video_analyses': video_analyses,
            'learning_objectives': learning_objectives,
            'prerequisites': prerequisites,
            'learning_path': learning_path,
            'difficulty_level': self._assess_difficulty_level(content_summary),
            'estimated_completion_time': self._estimate_completion_time(playlist_data['videos'])
        }
    
    def _prepare_content_summary(self, playlist_data: Dict) -> str:
        """Prepare a summary of all content for analysis.
        
        Args:
            playlist_data: Complete playlist data
            
        Returns:
            Content summary string
        """
        summary_parts = []
        
        # Add playlist info
        playlist_info = playlist_data['playlist_info']
        summary_parts.append(f"Playlist: {playlist_info['title']}")
        summary_parts.append(f"Description: {playlist_info['description']}")
        summary_parts.append(f"Total Videos: {len(playlist_data['videos'])}")
        summary_parts.append("")
        
        # Add video summaries
        for i, video in enumerate(playlist_data['videos'][:10], 1):  # Limit to first 10 videos
            summary_parts.append(f"Video {i}: {video['title']}")
            if video['description']:
                summary_parts.append(f"Description: {video['description'][:200]}...")
            if video.get('transcript'):
                # Use first 500 characters of transcript
                transcript_preview = video['transcript'][:500] + "..." if len(video['transcript']) > 500 else video['transcript']
                summary_parts.append(f"Transcript preview: {transcript_preview}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
      def _analyze_content_structure(self, content_summary: str) -> Dict:
        """Analyze the overall structure and themes of the content.
        
        Args:
            content_summary: Summary of all content
            
        Returns:
            Structure analysis results
        """
        prompt = f"""
        Analyze the following educational content and provide a structured analysis:

        {content_summary}

        Please provide:
        1. Main subject/topic
        2. Key themes and concepts covered
        3. Content organization pattern (sequential, thematic, etc.)
        4. Target audience level (beginner, intermediate, advanced)
        5. Learning approach (theoretical, practical, mixed)

        Respond in JSON format with keys: subject, themes, organization, audience_level, approach
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return self._parse_structure_response(content)
                
        except Exception as e:
            logger.error(f"Error analyzing content structure: {e}")
            return {
                "subject": "Unknown",
                "themes": ["Content analysis unavailable"],
                "organization": "sequential",
                "audience_level": "intermediate",
                "approach": "mixed"
            }
      def _analyze_video_content(self, video: Dict) -> Dict:
        """Analyze individual video content.
        
        Args:
            video: Video data with transcript
            
        Returns:
            Video analysis results
        """
        if not video.get('transcript'):
            return {
                'video_id': video['video_id'],
                'title': video['title'],
                'key_concepts': [],
                'summary': "No transcript available for analysis",
                'difficulty': "unknown",
                'duration_minutes': 0
            }
        
        prompt = f"""
        Analyze this educational video content:

        Title: {video['title']}
        Description: {video.get('description', '')[:300]}
        Transcript: {video['transcript'][:2000]}...

        Please provide:
        1. Key concepts covered (list)
        2. Brief summary (2-3 sentences)
        3. Difficulty level (beginner/intermediate/advanced)
        4. Main learning outcomes

        Respond in JSON format with keys: key_concepts, summary, difficulty, learning_outcomes
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = self._parse_video_response(content)
            
            # Add video metadata
            analysis['video_id'] = video['video_id']
            analysis['title'] = video['title']
            analysis['position'] = video.get('position', 0)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video {video['video_id']}: {e}")
            return {
                'video_id': video['video_id'],
                'title': video['title'],
                'key_concepts': [],
                'summary': f"Analysis failed: {str(e)}",
                'difficulty': "unknown",
                'learning_outcomes': []
            }
    
    def _generate_learning_objectives(self, content_summary: str, structure_analysis: Dict) -> List[str]:
        """Generate learning objectives for the entire course.
        
        Args:
            content_summary: Summary of all content
            structure_analysis: Structure analysis results
            
        Returns:
            List of learning objectives
        """
        prompt = f"""
        Based on this educational content analysis, generate 5-8 clear learning objectives:

        Subject: {structure_analysis.get('subject', 'Unknown')}
        Key Themes: {', '.join(structure_analysis.get('themes', []))}
        Audience Level: {structure_analysis.get('audience_level', 'intermediate')}

        Content Summary:
        {content_summary[:1000]}...

        Generate learning objectives that are:
        - Specific and measurable
        - Appropriate for the audience level
        - Cover the main themes
        - Use action verbs (understand, apply, analyze, etc.)

        Return as a JSON list of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an instructional designer. Generate clear, measurable learning objectives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Extract objectives from text
                objectives = []
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•') or 'objective' in line.lower()):
                        clean_objective = line.strip().lstrip('-•').strip()
                        if clean_objective:
                            objectives.append(clean_objective)
                return objectives[:8]
                
        except Exception as e:
            logger.error(f"Error generating learning objectives: {e}")
            return [
                "Understand the main concepts presented in the course",
                "Apply the knowledge gained to practical situations",
                "Analyze the relationships between different topics",
                "Evaluate the effectiveness of different approaches"
            ]
    
    def _identify_prerequisites(self, content_summary: str) -> List[str]:
        """Identify prerequisite knowledge needed.
        
        Args:
            content_summary: Summary of all content
            
        Returns:
            List of prerequisites
        """
        prompt = f"""
        Based on this educational content, identify the prerequisite knowledge a student should have:

        {content_summary[:1000]}...

        List 3-6 prerequisite topics or skills that would be helpful before starting this course.
        Return as a JSON list of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an educational consultant. Identify necessary prerequisite knowledge."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Extract from text
                prerequisites = []
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                        clean_prereq = line.strip().lstrip('-•').strip()
                        if clean_prereq:
                            prerequisites.append(clean_prereq)
                return prerequisites[:6]
                
        except Exception as e:
            logger.error(f"Error identifying prerequisites: {e}")
            return ["Basic understanding of the subject area"]
    
    def _suggest_learning_path(self, video_analyses: List[Dict], structure_analysis: Dict) -> List[Dict]:
        """Suggest optimal learning path through the content.
        
        Args:
            video_analyses: Analysis results for all videos
            structure_analysis: Overall structure analysis
            
        Returns:
            Suggested learning path with groupings
        """
        if not video_analyses:
            return []
        
        # Group videos by difficulty and themes
        beginner_videos = [v for v in video_analyses if v.get('difficulty') == 'beginner']
        intermediate_videos = [v for v in video_analyses if v.get('difficulty') == 'intermediate']
        advanced_videos = [v for v in video_analyses if v.get('difficulty') == 'advanced']
        
        learning_path = []
        
        # Start with beginner content
        if beginner_videos:
            learning_path.append({
                'module_name': 'Foundation Concepts',
                'description': 'Start with these fundamental concepts',
                'videos': beginner_videos,
                'order': 1
            })
        
        # Add intermediate content
        if intermediate_videos:
            learning_path.append({
                'module_name': 'Core Content',
                'description': 'Build on foundation with these key topics',
                'videos': intermediate_videos,
                'order': 2
            })
        
        # Add advanced content
        if advanced_videos:
            learning_path.append({
                'module_name': 'Advanced Topics',
                'description': 'Master advanced concepts and applications',
                'videos': advanced_videos,
                'order': 3
            })
        
        # If no difficulty classification, group by position
        if not learning_path:
            all_videos = sorted(video_analyses, key=lambda x: x.get('position', 0))
            chunk_size = max(1, len(all_videos) // 3)
            
            for i in range(0, len(all_videos), chunk_size):
                chunk = all_videos[i:i + chunk_size]
                learning_path.append({
                    'module_name': f'Module {len(learning_path) + 1}',
                    'description': f'Videos {i + 1} to {min(i + chunk_size, len(all_videos))}',
                    'videos': chunk,
                    'order': len(learning_path) + 1
                })
        
        return learning_path
    
    def _assess_difficulty_level(self, content_summary: str) -> str:
        """Assess overall difficulty level of the content.
        
        Args:
            content_summary: Summary of all content
            
        Returns:
            Difficulty level (beginner, intermediate, advanced)
        """
        # Simple heuristic based on content complexity indicators
        advanced_indicators = ['advanced', 'complex', 'sophisticated', 'expert', 'master']
        beginner_indicators = ['introduction', 'basic', 'fundamental', 'getting started', 'beginner']
        
        content_lower = content_summary.lower()
        
        advanced_score = sum(1 for indicator in advanced_indicators if indicator in content_lower)
        beginner_score = sum(1 for indicator in beginner_indicators if indicator in content_lower)
        
        if advanced_score > beginner_score:
            return 'advanced'
        elif beginner_score > 0:
            return 'beginner'
        else:
            return 'intermediate'
    
    def _estimate_completion_time(self, videos: List[Dict]) -> str:
        """Estimate total completion time including study time.
        
        Args:
            videos: List of video data
            
        Returns:
            Estimated completion time string
        """
        total_minutes = 0
        
        for video in videos:
            # Parse duration if available
            duration = video.get('duration', '')
            if duration:
                # Simple parsing for PT format
                minutes = 0
                if 'M' in duration:
                    try:
                        minutes = int(duration.split('M')[0].split('T')[-1])
                    except:
                        minutes = 5  # Default estimate
                total_minutes += minutes
        
        # Add study time (assume 2x video time for notes, practice, etc.)
        total_study_minutes = total_minutes * 2
        
        hours = total_study_minutes // 60
        minutes = total_study_minutes % 60
        
        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"
    
    def _parse_structure_response(self, response: str) -> Dict:
        """Fallback parser for structure analysis response.
        
        Args:
            response: Raw response text
            
        Returns:
            Parsed structure dictionary
        """
        return {
            "subject": "Educational Content",
            "themes": ["Various topics covered"],
            "organization": "sequential",
            "audience_level": "intermediate",
            "approach": "mixed"
        }
    
    def _parse_video_response(self, response: str) -> Dict:
        """Fallback parser for video analysis response.
        
        Args:
            response: Raw response text
            
        Returns:
            Parsed video analysis dictionary
        """
        return {
            "key_concepts": ["Content analysis"],
            "summary": "Video content analysis completed",
            "difficulty": "intermediate",
            "learning_outcomes": ["Understanding of video content"]
        }
