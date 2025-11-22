# Troubleshooting Guide

## Common Issues & Solutions

### 1. LLM Connection Issues

**Problem**: "Failed to initialize LLM client"

**Solutions**:
- Verify API keys in .env file
- Check internet connection
- Ensure API key has correct permissions
- Try switching LLM provider in config

```bash
# Test API connectivity
curl -X GET https://api.openrouter.ai/api/v1/models
```

### 2. Rate Limiting

**Problem**: "Rate limit exceeded" error

**Solutions**:
- Wait 60 seconds before retrying
- Increase RATE_LIMIT_REQUESTS in .env
- Use different IP address
- Implement exponential backoff in client

### 3. Voice Input Not Working

**Problem**: Speech recognition fails

**Solutions**:
- Use HTTPS (required for Web Speech API)
- Check browser permissions
- Ensure microphone is connected
- Try different browser (Chrome/Edge recommended)
- Check browser console for errors

### 4. Export Failures

**Problem**: Export returns error

**Solutions**:
- Verify output directory exists and is writable
- Check disk space
- Ensure file permissions are correct
- Try different export format

```bash
# Create output directory
mkdir -p output
chmod 755 output
```

### 5. Authentication Issues

**Problem**: Google OAuth login fails

**Solutions**:
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Check redirect URI matches Google Console settings
- Clear browser cookies
- Try incognito/private mode
- Verify Google API is enabled

### 6. Performance Issues

**Problem**: Slow response times

**Solutions**:
- Enable caching: CACHE_ENABLED=true
- Reduce number of agents (modify orchestrator)
- Increase AGENT_TIMEOUT value
- Check system resources (CPU, memory)
- Monitor with /api/performance endpoint

### 7. Frontend Not Loading

**Problem**: Blank page or 404 errors

**Solutions**:
- Check static files exist in static/ directory
- Verify Tailwind CSS CDN is accessible
- Check browser console for errors
- Clear browser cache
- Try different browser

### 8. Database/Cache Issues

**Problem**: Cache errors or data not persisting

**Solutions**:
- Clear .cache directory
- Verify .cache directory permissions
- Check disk space
- Disable cache if problematic: CACHE_ENABLED=false

### 9. CORS Errors

**Problem**: "CORS policy" errors in browser

**Solutions**:
- Verify CORS middleware is enabled
- Check allow_origins setting
- Use proxy for development
- Ensure requests use correct headers

### 10. Memory Leaks

**Problem**: Application memory usage increases over time

**Solutions**:
- Restart application periodically
- Clear old telemetry data
- Reduce cache TTL
- Monitor with /api/performance
- Check for circular references in code

## Debug Mode

Enable detailed logging:

```python
# In app/core/config.py
LOG_LEVEL=DEBUG
```

## Performance Tuning

### For High Traffic
```env
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=60
CACHE_ENABLED=true
CACHE_TTL=7200
```

### For Low Resources
```env
RATE_LIMIT_REQUESTS=50
CACHE_ENABLED=false
AGENT_TIMEOUT=15
```

## Monitoring

Check system health:
```bash
# Health check
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/api/performance

# Analytics
curl http://localhost:8000/api/analytics
```

## Logs

View application logs:
```bash
# Docker logs
docker-compose logs -f app

# Local logs
tail -f app.log
```

## Getting Help

1. Check this troubleshooting guide
2. Review application logs
3. Check GitHub issues
4. Contact support with:
   - Error message
   - Steps to reproduce
   - System information
   - Relevant logs
