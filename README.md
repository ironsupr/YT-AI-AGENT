# YouTube Playlist Learning Module Generator

An AI-powered agent that processes YouTube playlist links to extract content and automatically organize it into structured learning modules for students.

## ✨ Features

- **🎯 AI-Powered Analysis**: Uses Google's Gemini AI to analyze video content and extract key concepts
- **📊 Playlist Processing**: Extracts playlist metadata, video information, and transcripts
- **📚 Smart Organization**: Automatically creates structured learning modules with clear progression
- **🎓 Student-Friendly**: Generates learning objectives, study guides, and practice materials
- **🌐 Web Interface**: Beautiful, responsive web interface for easy playlist processing
- **📱 Multiple Formats**: Outputs in HTML, JSON, and Markdown formats
- **⚡ Fast Processing**: Efficient processing with progress tracking

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# The system will automatically create a virtual environment
pip install -r requirements.txt
```

### 2. Get API Keys

#### YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **YouTube Data API v3**
4. Create credentials (API Key)
5. Copy your API key

#### Google AI API Key (Gemini)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign up or log in with your Google account
3. Create a new API key
4. Copy your API key

### 3. Environment Setup
Create a `.env` file in the project root:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Optional configurations
GEMINI_MODEL=gemini-1.5-flash
FLASK_DEBUG=True
```

### 4. Test Installation
```bash
python test_setup.py
```
This will verify that everything is set up correctly.

## 📖 Usage

### 🌐 Web Interface (Recommended)
```bash
python app.py
```
Then open http://localhost:5000 in your browser for an interactive experience.

### 💻 Command Line Interface
```bash
# Basic usage
python main.py "https://www.youtube.com/playlist?list=PLxxx"

# With options
python main.py --url "playlist_url" --max-videos 20 --output "./my_course"

# Test API connections
python main.py test
```

#### CLI Options
- `--max-videos`: Maximum number of videos to process (default: 50)
- `--output`: Output directory for generated files (default: output)
- `--model`: Gemini model to use (default: gemini-1.5-flash)
- `--verbose`: Enable detailed logging

## Project Structure

```
.
├── main.py              # Main CLI application
├── app.py              # Flask web application
├── src/
│   ├── __init__.py
│   ├── youtube_extractor.py    # YouTube API integration
│   ├── content_analyzer.py     # AI content analysis
│   ├── module_generator.py     # Learning module creation
│   └── utils.py               # Utility functions
├── templates/
│   └── index.html             # Web interface template
├── static/
│   ├── style.css             # Styling
│   └── script.js             # Frontend JavaScript
├── output/                   # Generated learning modules
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## 📁 Generated Output

The system creates comprehensive learning materials:

### 📄 Interactive HTML Guide
- Beautiful, responsive course interface
- Module navigation and progress tracking
- Embedded video links and notes sections
- Downloadable for offline use

### 📊 Structured JSON Data
- Complete course metadata and structure
- Easy integration with learning management systems
- Programmatic access to all content

### 📝 Markdown Documentation
- Clean, readable course documentation
- Compatible with GitHub, GitLab, and documentation systems
- Easy to edit and customize

## 🎯 What You Get

### 📚 Complete Course Structure
- **Course Overview**: Title, description, difficulty level, estimated time
- **Learning Objectives**: Clear, measurable goals for students
- **Prerequisites**: Knowledge students should have before starting
- **Module Organization**: Logical progression through topics

### 🎓 Learning Modules
Each module includes:
- **Video Analysis**: AI-generated summaries and key concepts
- **Learning Objectives**: Specific goals for each module
- **Study Activities**: Suggested exercises and practice
- **Progress Tracking**: Completion status and time estimates
- **Reflection Questions**: Prompts for deeper thinking

### 📋 Study Materials
- **Study Guide**: Comprehensive overview and tips
- **Quiz Questions**: Generated based on content analysis
- **Progress Tracker**: Track completion and study streaks
- **Glossary**: Key terms and definitions
- **Additional Resources**: Curated links and references

## 🔧 Advanced Configuration

### Custom AI Models
```env
# Use different Gemini models
GEMINI_MODEL=gemini-1.5-pro  # More capable but slower
GEMINI_MODEL=gemini-1.5-flash  # Faster and efficient
```

### Processing Limits
```bash
# Process only first 10 videos for quick testing
python main.py --max-videos 10 "playlist_url"

# Process up to 100 videos for comprehensive courses
python main.py --max-videos 100 "playlist_url"
```

### Output Customization
```bash
# Specify custom output directory
python main.py --output "/path/to/custom/directory" "playlist_url"

# Use different AI model
python main.py --model "gemini-1.5-pro" "playlist_url"
```

## 🛠️ Project Structure

```
YouTube-Playlist-Learning-Generator/
├── main.py                    # CLI application
├── app.py                     # Flask web application
├── test_setup.py             # Installation test script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This documentation
│
├── src/                     # Core application modules
│   ├── __init__.py
│   ├── youtube_extractor.py    # YouTube API integration
│   ├── content_analyzer.py     # AI content analysis
│   ├── module_generator.py     # Learning module creation
│   └── utils.py               # Utility functions
│
├── templates/               # Web interface templates
│   └── index.html            # Main web interface
│
├── static/                  # Web interface assets
│   ├── style.css            # Styling
│   └── script.js            # Frontend JavaScript
│
├── output/                  # Generated course materials
│   ├── course_data.json     # Complete course data
│   ├── course_guide.html    # Interactive HTML guide
│   └── course_guide.md      # Markdown documentation
│
└── .github/                 # GitHub configuration
    └── copilot-instructions.md  # AI coding assistant instructions
```

## 🔍 Example Workflow

1. **Input**: Provide YouTube playlist URL
2. **Extraction**: System downloads playlist metadata and video transcripts
3. **Analysis**: AI analyzes content to identify key concepts and themes
4. **Organization**: Content is organized into logical learning modules
5. **Generation**: Comprehensive course materials are created
6. **Output**: Multiple formats available for different use cases

## 🚨 Troubleshooting

### Common Issues

**❌ "Import errors" or "Module not found"**
- Run `python test_setup.py` to verify installation
- Ensure you're using the correct Python environment
- Try reinstalling dependencies: `pip install -r requirements.txt`

**❌ "API key not found"**
- Create `.env` file with your API keys (copy from `.env.example`)
- Ensure API keys are correctly set in environment variables
- Test API connections: `python main.py test`

**❌ "Invalid playlist URL"**
- Ensure URL contains `list=` parameter
- Check that playlist is public and accessible
- Try with a different playlist URL

**❌ "No transcripts available"**
- Some videos may not have transcripts
- System will still process videos with descriptions
- Consider playlists with educational content (often have transcripts)

### Performance Tips

- **Start Small**: Test with `--max-videos 5` for quick validation
- **Choose Quality Playlists**: Educational channels often have better transcripts
- **Monitor Usage**: Both APIs have rate limits and costs
- **Use Appropriate Models**: GPT-3.5-turbo is faster and cheaper than GPT-4

## 📈 Limitations

- **Transcript Dependency**: Best results with videos that have transcripts
- **API Costs**: OpenAI API usage incurs costs based on tokens processed
- **Rate Limits**: YouTube API has daily quotas and rate limits
- **Language Support**: Currently optimized for English content
- **Video Length**: Very long videos may hit token limits

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

### Development Setup
1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables
5. Run tests: `python test_setup.py`

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Google** for Gemini AI models enabling intelligent content analysis
- **Google** for YouTube Data API providing playlist access
- **YouTube Transcript API** for transcript extraction capabilities
- **Flask** for the web framework
- **All contributors** who help improve this tool

---

**🚀 Ready to transform your YouTube playlists into structured learning experiences?**

Start by running: `python test_setup.py` to verify your installation, then try the web interface with `python app.py`!
