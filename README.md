# YouTube Playlist Learning Module Generator

An AI-powered tool that transforms YouTube playlists into structured learning modules using Google's Gemini AI.

## ✨ Features

- **🎯 AI-Powered Analysis**: Uses Google Gemini to analyze video content and extract key concepts
- **📊 Smart Processing**: Extracts playlist metadata, video information, and transcripts
- **📚 Learning Modules**: Automatically creates structured modules with clear progression
- **🌐 Web Interface**: Beautiful, responsive interface for easy playlist processing
- **🔥 Firebase Integration**: Optional persistent storage and analysis caching
- **📱 Multiple Formats**: Outputs in HTML, JSON, and Markdown formats
- **⚡ Performance**: Fast processing with progress tracking and smart caching

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone <repository-url>
cd youtube-playlist-generator
pip install -r requirements.txt
```

### 2. Get API Keys

**YouTube Data API:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create an API key

**Google AI API (Gemini):**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key

### 3. Configure Environment
Create `.env` file:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Optional: Firebase integration
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/service-account.json
```

### 4. Run
```bash
# Web interface (recommended)
python app.py

# Command line
python main.py "https://www.youtube.com/playlist?list=PLxxx"
```

## 📖 Usage

### Web Interface
1. Start the server: `python app.py`
2. Open http://localhost:5000
3. Enter a YouTube playlist URL
4. Wait for processing and download results

### Command Line
```bash
# Basic usage
python main.py "https://www.youtube.com/playlist?list=PLxxx"

# With options
python main.py --url "playlist_url" --max-videos 20 --output "./course"
```

**Options:**
- `--max-videos`: Limit number of videos (default: 50)
- `--output`: Output directory (default: output)
- `--model`: Gemini model (default: gemini-1.5-flash)
- `--verbose`: Enable detailed logging

## 🔥 Firebase Integration (Optional)

Add persistent storage and smart caching:

1. Create a Firebase project with Firestore enabled
2. Download service account JSON
3. Set `FIREBASE_SERVICE_ACCOUNT_PATH` in `.env`
4. Restart the application

**Benefits:**
- Store playlist data and analysis results
- Avoid reprocessing the same content
- Browse and manage saved playlists
- RESTful API for data access

📚 **See [FIREBASE_INTEGRATION.md](FIREBASE_INTEGRATION.md) for detailed setup**

## 📁 Project Structure

```
├── main.py                   # CLI application
├── app.py                   # Web application
├── src/
│   ├── youtube_extractor.py  # YouTube API integration
│   ├── content_analyzer.py   # AI content analysis
│   ├── module_generator.py   # Learning module creation
│   ├── firebase_service.py   # Firebase integration
│   └── utils.py              # Utility functions
├── templates/               # Web interface templates
├── static/                  # CSS and JavaScript
└── output/                  # Generated learning modules
```

## 📊 Generated Output

The system creates:

- **Interactive HTML**: Complete course with navigation and progress tracking
- **JSON Data**: Structured data for integration with other systems
- **Markdown**: Clean documentation format

Each output includes:
- Course overview and objectives
- Module breakdown with video links
- Learning objectives and prerequisites
- Study guides and key concepts

## 🧪 Testing

```bash
# Test installation
python test_setup.py

# Test with sample playlist
python main.py "https://www.youtube.com/playlist?list=PLWKjhJtqVAbleDe3_ZA8h3AO2rXar-q2V"
```

## ⚙️ Requirements

- Python 3.8+
- YouTube Data API v3 key
- Google AI API key (Gemini)
- Optional: Firebase project for persistence

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🛠️ Troubleshooting

**Common Issues:**
- **API Key Errors**: Verify keys are correctly set in `.env`
- **Quota Exceeded**: YouTube API has daily limits
- **Transcript Issues**: Not all videos have transcripts available
- **Firebase Errors**: Check service account permissions

**Support:**
- Check the logs for detailed error messages
- Ensure all dependencies are installed
- Verify API keys have proper permissions

---

Transform YouTube playlists into structured learning experiences with AI! 🎓✨
