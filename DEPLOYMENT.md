# TravelAI Deployment Guide

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
python run.py
```

Visit http://localhost:8000 in your browser.

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8000
```

## Environment Configuration

### Required Variables

```env
# LLM Configuration
OPENROUTER_API_KEY=your_key_here
LLM_PROVIDER=openrouter
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Server Configuration
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Features
CACHE_ENABLED=true
CACHE_TTL=3600
ENABLE_TELEMETRY=true
ENABLE_ANALYTICS=true
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/TLS with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Performance Optimization

### Caching Strategy

- Enable Redis for distributed caching
- Set appropriate TTL values
- Monitor cache hit rates

### Database Optimization

- Index frequently queried fields
- Use connection pooling
- Regular maintenance and cleanup

### Frontend Optimization

- Minify CSS and JavaScript
- Enable gzip compression
- Use CDN for static assets
- Implement service workers

## Monitoring & Logging

### Application Monitoring

```bash
# Check health
curl http://localhost:8000/health

# View performance metrics
curl http://localhost:8000/api/performance

# Get analytics
curl http://localhost:8000/api/analytics
```

### Log Aggregation

Configure centralized logging with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- CloudWatch (AWS)
- Stackdriver (GCP)

## Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Set secure CORS headers
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Enable CSRF protection
- [ ] Set secure cookies (HttpOnly, Secure, SameSite)
- [ ] Regular security audits
- [ ] Keep dependencies updated

## Scaling

### Horizontal Scaling

- Use load balancer (nginx, HAProxy)
- Deploy multiple instances
- Use shared cache (Redis)
- Use shared database

### Vertical Scaling

- Increase server resources
- Optimize code performance
- Use async processing
- Implement caching

## Backup & Recovery

```bash
# Backup database
pg_dump database_name > backup.sql

# Backup configuration
tar -czf config_backup.tar.gz .env

# Restore from backup
psql database_name < backup.sql
```

## Troubleshooting

### High Memory Usage

- Check for memory leaks
- Reduce cache size
- Implement garbage collection
- Monitor with `top` or `htop`

### Slow Response Times

- Check database queries
- Enable caching
- Use CDN
- Optimize images
- Profile with `cProfile`

### Connection Issues

- Check firewall rules
- Verify DNS resolution
- Check API rate limits
- Review error logs

## Support

For issues and questions:
1. Check documentation
2. Review logs
3. Check GitHub issues
4. Contact support team
