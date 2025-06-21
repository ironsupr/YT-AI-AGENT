# YouTube Course Generator Agent

A standalone AI agent that converts YouTube playlists into comprehensive course structures using Google's Gemini AI and YouTube Data API.

## Features

- **Playlist Analysis**: Extracts metadata, video details, and transcripts from YouTube playlists
- **AI-Powered Course Generation**: Uses Google Gemini to create structured learning content
- **Comprehensive Output**: Generates complete course structures with modules, lessons, assignments, and final exams
- **Multiple Content Types**: Supports video lessons, text content, quizzes, and projects
- **Robust Error Handling**: Graceful fallbacks and detailed logging
- **JSON Output**: Structured data format compatible with learning management systems

## Prerequisites

1. **Python 3.8+**
2. **API Keys**:
   - YouTube Data API v3 key
   - Google AI (Gemini) API key
3. **Required Python packages** (see requirements.txt):
   - google-generativeai
   - google-api-python-client
   - youtube-transcript-api
   - python-dotenv

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file in the parent directory with:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   GOOGLE_AI_API_KEY=your_gemini_api_key_here
   ```

3. **Get API Keys**:
   - **YouTube Data API**: Go to [Google Cloud Console](https://console.cloud.google.com/), enable YouTube Data API v3, and create credentials
   - **Google AI API**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### Command Line

```bash
# Basic usage
python yt_agent.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Specify maximum number of videos
python yt_agent.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" 10

# Interactive mode
python yt_agent.py
```

### Programmatic Usage

```python
from yt_agent import YouTubeAgent

# Initialize agent
agent = YouTubeAgent(youtube_api_key, gemini_api_key, output_dir="output")

# Process playlist
output_file = agent.process_playlist(playlist_url, max_videos=20)

# Get course summary
with open(output_file, 'r') as f:
    course_data = json.load(f)
summary = agent.get_course_summary(course_data)
print(summary)
```

## Output Structure

The agent generates a comprehensive JSON file with the following structure:

```json
{
  "course": {
    "title": "Course Title",
    "description": "Course description",
    "category": "Programming",
    "level": "Beginner",
    "price": 99.99,
    "duration": "8 weeks",
    "instructor": "Instructor Name",
    "tags": ["tag1", "tag2"],
    "prerequisites": ["prerequisite1"],
    "learningObjectives": ["objective1", "objective2"],
    "estimatedHours": 40
  },
  "modules": [
    {
      "id": "module-1",
      "title": "Module Title",
      "description": "Module description",
      "lessons": [
        {
          "id": "lesson-1-1",
          "title": "Lesson Title",
          "type": "video|text|quiz|project",
          "content": {...},
          "resources": [...]
        }
      ]
    }
  ],
  "assignments": [...],
  "finalExam": {...},
  "metadata": {...}
}
```

## Testing

Run the test script to verify everything is working:

```bash
python test_agent.py
```

## Configuration

The agent can be configured by modifying the following parameters in the code:

- **Generation settings**: Temperature, top_p, top_k for AI responses
- **Module organization**: Number of modules (3-6), videos per module
- **Content limits**: Transcript length, description length
- **Output format**: JSON structure and metadata

## Limitations

1. **YouTube API Quotas**: Limited by YouTube Data API daily quotas
2. **Transcript Availability**: Not all videos have transcripts available
3. **AI Response Variability**: Gemini responses may vary in quality
4. **Public Playlists Only**: Can only process public YouTube playlists

## Error Handling

The agent includes robust error handling for:

- Invalid playlist URLs
- API rate limits and errors
- Missing transcripts
- JSON parsing failures
- Network connectivity issues

## Logging

Detailed logging is provided for:

- Playlist extraction progress
- AI generation steps
- Error conditions
- Performance metrics

## Files

- `yt_agent.py`: Main agent script
- `test_agent.py`: Test script
- `output/`: Directory for generated course files
- `README.md`: This documentation

## Support

For issues or questions:

1. Check the logs for error details
2. Verify API keys are correctly set
3. Ensure the playlist is public and accessible
4. Test with a smaller number of videos first

## Version History

- **v1.0.0**: Initial release with core functionality
- **v2.0.0**: Enhanced course generation with improved AI prompts
