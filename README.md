# 🎙️ AI News Reporter

> An intelligent news broadcasting system that analyzes social media discussions and generates professional audio news reports using AI.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/AI-Groq-purple.svg)](https://groq.com)

## 🚀 Overview

AI News Reporter is a cutting-edge application that automatically generates professional news broadcasts by analyzing real-time social media discussions. The system combines advanced AI language models with text-to-speech technology to deliver broadcast-quality audio news reports on any topic.

### ✨ Key Features

- **🔍 Social Media Analysis**: Scrapes and analyzes discussions from Reddit, Twitter, and forums
- **🤖 AI-Powered Content Generation**: Uses Groq's Gemma2-9B-IT model for intelligent news synthesis
- **🎵 Audio Broadcasting**: Converts text to natural-sounding speech using Google Text-to-Speech
- **📱 Modern Web Interface**: Clean, responsive Streamlit frontend
- **⚡ Real-time Processing**: Fast API backend with async processing
- **💰 Cost-Effective**: Uses free/low-cost AI services (Groq, gTTS, BrightData)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   AI Services   │
│   Frontend      │◄──►│    Backend      │◄──►│   (Groq API)    │
│   (Port 8080)   │    │   (Port 1234)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐               │
         │              │ Social Media    │               │
         └──────────────►│ Analysis Engine │◄──────────────┘
                        │ (Reddit/Twitter)│
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Text-to-Speech  │
                        │ (Google gTTS)   │
                        └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: Streamlit
- **AI/ML**: Groq API (Gemma2-9B-IT model)
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Web Scraping**: BrightData, BeautifulSoup
- **Social Media**: Reddit API, Model Context Protocol (MCP)
- **HTTP Client**: HTTPX for async requests

## 📋 Prerequisites

- Python 3.9 or higher
- Virtual environment (recommended)
- API keys for:
  - Groq API (free tier available)
  - BrightData (for web scraping)
  - ElevenLabs (optional, premium TTS)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-news-reporter.git
cd ai-news-reporter
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Groq Configuration (Required)
GROQ_API_KEY="your_groq_api_key_here"

# Web Scraping Configuration (Required)
WEB_UNLOCKER_ZONE="your_brightdata_zone"
BRIGHTDATA_API_KEY="your_brightdata_api_key"

# ElevenLabs Configuration (Optional - Premium TTS)
ELEVENLABS_API_KEY="your_elevenlabs_key"
```

### 5. Start the Backend Server

```bash
python backend.py
```

The API will be available at `http://127.0.0.1:1234`

### 6. Launch the Frontend

```bash
streamlit run frontend.py --server.port 8080
```

Access the application at `http://localhost:8080`

## 📚 API Documentation

### Generate News Audio

**Endpoint**: `POST /generate-news-audio`

**Request Body**:
```json
{
  "topics": ["technology", "politics", "finance"],
  "source_type": "social_media"
}
```

**Response**: MP3 audio file

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "message": "Server is running"
}
```

### Test Groq Integration

**Endpoint**: `POST /test-groq`

**Response**:
```json
{
  "status": "success",
  "summary": "Generated news summary..."
}
```

## 🐛 Challenges Faced & Solutions

### 1. **API Cost Management**
**Problem**: Initial implementation used Anthropic Claude API which had insufficient credits for development.

**Solution**: Migrated to Groq API's free tier with Gemma2-9B-IT model, providing:
- Free API access with generous rate limits
- High-quality language model performance
- Faster response times than local models

### 2. **Model Name Configuration Issues**
**Problem**: Groq API returned 404 errors due to incorrect model name format.

**Initial Error**: Using `"gemma-2-9b-it"` (with hyphens)
**Solution**: Corrected to `"gemma2-9b-it"` (no hyphens in "gemma2")

### 3. **File Encoding Corruption**
**Problem**: Manual file edits caused null byte insertion and UTF-8 encoding issues.

**Solution**: 
- Implemented systematic file recreation with proper UTF-8 encoding
- Used PowerShell here-strings for safe file operations
- Added file validation checks

### 4. **Import Dependencies & Module Structure**
**Problem**: Complex interdependencies between modules causing import failures.

**Solution**:
- Renamed `reddit_scraper.py` to `social_analyzer.py` for broader scope
- Implemented backward compatibility functions
- Streamlined import structure
- Enhanced error handling

### 5. **Local Model Dependencies**
**Problem**: Initial Ollama integration required local model installation and management.

**Solution**:
- Completely removed Ollama dependencies
- Migrated all AI operations to cloud-based Groq API
- Simplified deployment and eliminated local resource requirements

### 6. **Audio Generation Costs**
**Problem**: ElevenLabs premium TTS service costs for development testing.

**Solution**:
- Implemented Google Text-to-Speech (gTTS) as primary TTS engine
- Kept ElevenLabs as optional premium upgrade
- Reduced operational costs to near-zero

## 📁 Project Structure

```
ai-news-reporter/
├── backend.py              # FastAPI server
├── frontend.py             # Streamlit web interface
├── models.py               # Pydantic data models
├── social_analyzer.py      # Social media analysis engine
├── utils.py                # Core utility functions
├── news_scraper.py         # Web scraping utilities
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── audio/                  # Generated audio files
└── README.md              # Project documentation
```

## 🔧 Configuration Options

### Source Types
- `"social_media"`: Reddit, Twitter, forums
- `"news"`: Traditional news websites
- `"both"`: Combined social media and news analysis

### AI Models
- **Primary**: Groq Gemma2-9B-IT (free)
- **Alternative**: OpenAI GPT (requires API key)

### Text-to-Speech Options
- **Free**: Google Text-to-Speech (gTTS)
- **Premium**: ElevenLabs (high-quality voices)

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Backend
python backend.py

# Terminal 2: Frontend
streamlit run frontend.py --server.port 8080
```

### Production Deployment
- **Backend**: Deploy FastAPI with Gunicorn/Uvicorn
- **Frontend**: Streamlit Cloud or Docker container
- **Database**: Optional Redis for caching
- **Monitoring**: Health check endpoints included

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing free access to high-quality language models
- **BrightData** for reliable web scraping infrastructure
- **Google** for free text-to-speech services
- **Streamlit** for the excellent web framework
- **FastAPI** for the high-performance backend framework

---

**Built with ❤️ for the future of AI-powered journalism**
