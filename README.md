# TravelAI 🌍✈️ - AI-Powered Travel Planning

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://pytest.org/)

A production-ready, AI-powered travel planning platform that leverages a sophisticated multi-agent architecture to generate personalized, comprehensive travel guides with real-time streaming updates.

## ✨ Features

### Core Capabilities
- **🤖 Multi-Agent AI Architecture**: 16+ specialized AI agents working in parallel (History, Weather, Itinerary, Culinary, Safety, Nightlife, and more)
- **⚡ Real-time Streaming**: Server-Sent Events (SSE) for live progress updates during guide generation
- **🧠 Dynamic LLM Support**: Seamlessly switch between Google Gemini, OpenRouter, and NVIDIA NIM
- **🎙️ Voice Interaction**: Integrated Text-to-Speech (TTS) and Speech-to-Text (STT) for hands-free experience
- **📱 Progressive Web App (PWA)**: Install as a native app on any device with offline support
- **🎨 Premium UI/UX**: Glassmorphism 2.0 design with 5 stunning themes, smooth animations, and responsive layout

### Production Quality
- **🔒 Enterprise Security**: CSP, HSTS, XSS protection, rate limiting, input sanitization
- **♿ WCAG 2.2 AA Accessibility**: Full keyboard navigation, screen reader support, focus management
- **🚀 High Performance**: Optimized for speed with lazy loading, code splitting, and caching strategies
- **📊 Comprehensive Testing**: 90%+ test coverage with unit, integration, and E2E tests
- **📈 SEO Optimized**: Rich meta tags, Open Graph, Twitter Cards, JSON-LD structured data

## 🛠️ Tech Stack

### Backend
- **Framework**: Python 3.11 + FastAPI + Uvicorn
- **Validation**: Pydantic v2 with strict typing
- **AI/LLM**: Google Gemini API, OpenRouter, NVIDIA NIM
- **Testing**: Pytest, pytest-cov, pytest-asyncio

### Frontend
- **Languages**: HTML5, Vanilla JavaScript (TypeScript-ready)
- **Styling**: Tailwind CSS 4, Custom CSS variables for theming
- **Icons**: Lucide Icons
- **PWA**: Service Worker with cache-first strategy

### DevOps
- **Containerization**: Docker + Docker Compose
- **Code Quality**: Black, Flake8, Mypy, Bandit
- **Security**: Safety, dependency scanning

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Docker (optional, for containerized deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/travelai.git
   cd travelai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here  # Optional
   NVIDIA_API_KEY=your_nvidia_api_key_here   # Optional
   ```

3. **Run with Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```
   
   The application will be available at http://localhost:8000

4. **OR Run Locally**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the server
   python run.py
   ```
   
   The application will be available at http://localhost:8000

## 🔌 API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key Endpoints

#### `POST /api/generate`
Generate a complete travel guide for a destination.

**Request:**
```json
{
  "destination": "Tokyo",
  "language": "en"
}
```

**Response:**
```json
{
  "status": "success",
  "destination": "Tokyo",
  "data": {
    "places": {...},
    "itinerary": {...},
    "food": {...},
    "weather": {...},
    ...
  },
  "timestamp": "2025-01-21T12:00:00"
}
```

#### `GET /api/stream`
Stream real-time updates during travel plan generation.

**Query Parameters:**
- `destination` (required): Destination name
- `mother_tongue` (optional): Language code (default: "en")

**Response:** Server-Sent Events stream

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "TravelAI",
  "version": "1.0.0"
}
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests with coverage
pytest tests/ --cov=app --cov-report=html

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run security tests
pytest tests/ -m security
```

### Code Quality Checks
```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

## 🚀 Deployment

### Docker Deployment
The application includes a production-ready Dockerfile and docker-compose configuration.

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables for Production
```env
# LLM Configuration
OPENROUTER_API_KEY=your_production_key
LLM_PROVIDER=openrouter

# Security
SECRET_KEY=generate_a_strong_random_secret_key
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Performance
CACHE_ENABLED=true
CACHE_TTL=3600

# Monitoring
ENABLE_TELEMETRY=true
ENABLE_ANALYTICS=true
LOG_LEVEL=INFO
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (PWA)                      │
│  HTML5 + Vanilla JS + Tailwind CSS + Service Worker    │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/SSE
┌────────────────┴────────────────────────────────────────┐
│                    FastAPI Server                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Middleware Stack                               │   │
│  │  • Security Headers  • Rate Limiting            │   │
│  │  • CORS  • Request Size Limit  • Correlation ID │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  API Endpoints                                  │   │
│  │  /api/generate  /api/stream  /health  /api/*   │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                 AI Orchestrator                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ History  │  │ Weather  │  │Itinerary │  ... 16+    │
│  │  Agent   │  │  Agent   │  │  Agent   │   Agents    │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│              LLM Providers                               │
│  Google Gemini  •  OpenRouter  •  NVIDIA NIM            │
└─────────────────────────────────────────────────────────┘
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && black app/ && flake8 app/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use Black for formatting (line length: 100)
- Add type hints to all functions
- Write docstrings for public APIs
- Maintain test coverage above 90%

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI inspired by modern design principles
- Icons by [Lucide](https://lucide.dev/)
- Fonts by [Google Fonts](https://fonts.google.com/)

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/travelai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/travelai/discussions)
- **Email**: support@travelai.app

## 🗺️ Roadmap

- [ ] Mobile apps (iOS & Android)
- [ ] Multi-language UI (currently English)
- [ ] User accounts and saved trips
- [ ] Collaborative trip planning
- [ ] Integration with booking platforms
- [ ] AI-powered budget optimization
- [ ] Real-time travel alerts

---

Made with ❤️ by the TravelAI Team
#   T r a v e l - A I  
 