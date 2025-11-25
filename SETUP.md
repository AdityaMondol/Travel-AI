# Leonore AI - Production Setup Guide

## Quick Start

### 1. Prerequisites
- Python 3.10+
- pip or conda
- NVIDIA API key (for LLM access)

### 2. Installation

```bash
# Clone repository
git clone <repo>
cd leonore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Database Setup

```bash
# Initialize database
python -c "from app.core.database import init_db; init_db()"
```

### 4. Run Application

```bash
# Development
python run.py

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Visit http://localhost:8000

## Configuration

### Environment Variables

```env
# Required
NVIDIA_API_KEY=your_key_here

# Optional
LLM_PROVIDER=nvidia  # or openrouter, google
DATABASE_URL=sqlite:///./leonore.db  # or postgresql://...
LOG_LEVEL=INFO
```

### Database Options

**SQLite (Default)**
```env
DATABASE_URL=sqlite:///./leonore.db
```

**PostgreSQL (Production)**
```bash
pip install psycopg2-binary
```

```env
DATABASE_URL=postgresql://user:password@localhost/leonore
```

## API Endpoints

### Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_1",
    "message": "Hello"
  }'
```

### Upload File
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf" \
  -F "session_id=session_1"
```

### Query Memory
```bash
curl http://localhost:8000/api/memory?query=test&limit=10
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Features

### Multi-Agent System
- Hierarchical agent spawning
- Specialist agents (Coder, Researcher, Analyst, etc.)
- Autonomous planning and execution
- Real-time reflection and optimization

### Memory System
- Persistent memory storage
- Semantic search
- Session-based context
- Memory statistics

### Streaming
- Real-time response streaming
- Heartbeat mechanism
- Error recovery
- Event-based architecture

### Production Features
- Request validation
- Rate limiting
- Error handling
- Comprehensive logging
- Health checks

## Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Deployment

### Docker

```bash
docker-compose up --build
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

### Environment-Specific

**Development**
```bash
python run.py
```

**Staging**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

**Production**
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Monitoring

### Logs
```bash
tail -f logs/leonore.log
```

### Metrics
- Agent activity
- Memory usage
- Response times
- Error rates

## Troubleshooting

### API Not Responding
1. Check NVIDIA_API_KEY is set
2. Verify network connectivity
3. Check logs: `tail -f logs/leonore.log`

### Database Errors
1. Ensure database is initialized
2. Check DATABASE_URL format
3. Verify database permissions

### Memory Issues
1. Clear old sessions: `python scripts/cleanup.py`
2. Optimize database: `python scripts/optimize_db.py`

## Performance Tuning

### Increase Concurrency
```env
RATE_LIMIT_REQUESTS=500
```

### Optimize Database
```bash
python scripts/optimize_db.py
```

### Enable Caching
```env
CACHE_ENABLED=true
CACHE_TTL=7200
```

## Security

### API Key Management
- Never commit .env files
- Use environment variables in production
- Rotate keys regularly

### Rate Limiting
- Default: 100 requests/minute
- Configurable per endpoint
- IP-based tracking

### Input Validation
- All inputs validated
- File size limits enforced
- SQL injection prevention

## Support

For issues and questions:
1. Check logs
2. Review documentation
3. Open GitHub issue
4. Contact support

## License

MIT
