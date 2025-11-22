# Docker Deployment Guide

## Prerequisites
- Docker installed and running
- Docker Compose installed
- .env file configured with API keys

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Build and Run
```bash
# Using docker-compose
docker-compose up --build

# Or using the provided script
bash docker-build.sh
```

### 3. Access Application
- Frontend: http://localhost:8000
- Health Check: http://localhost:8000/health

### 4. Stop Container
```bash
docker-compose down

# Or using the provided script
bash docker-stop.sh
```

## Docker Commands

### View Logs
```bash
docker-compose logs -f app
```

### Rebuild Image
```bash
docker-compose build --no-cache
```

### Remove Everything
```bash
docker-compose down -v
docker rmi travelai:latest
```

## Production Deployment

### Environment Variables
Set these in production:
- OPENROUTER_API_KEY: Your API key
- LLM_PROVIDER: openrouter
- LOG_LEVEL: INFO
- CACHE_ENABLED: true

### Resource Limits
Current limits in docker-compose.yml:
- CPU: 2 cores (limit), 1 core (reservation)
- Memory: 2GB (limit), 512MB (reservation)

Adjust based on your infrastructure.

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
# ports:
#   - "8001:8000"
```

### Container Won't Start
```bash
docker-compose logs app
```

### Health Check Failing
```bash
docker exec travelai-app curl http://localhost:8000/health
```

## Performance Tuning

### Increase Workers
Edit Dockerfile CMD:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Enable Caching
Set in .env:
```
CACHE_ENABLED=true
CACHE_TTL=7200
```
