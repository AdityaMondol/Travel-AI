# Leonore AI

Production-ready autonomous agent platform with NVIDIA NIM integration, multi-agent orchestration, and comprehensive safety governance.

## Architecture

### Backend (Python)
- **FastAPI** gateway with ASGI/uvicorn
- **NVIDIA NIM** integration for LLM inference
- **LangChain/LangGraph** for agent orchestration
- **Multi-agent system** with specialist agents (researcher, coder, analyst, strategist, designer)
- **Vector DB** support (Milvus, Weaviate, Pinecone) for RAG
- **Redis** for caching and job queues
- **Celery** for async task processing
- **PostgreSQL** for persistent storage

### Frontend (React)
- **React 18** with TypeScript
- **Tailwind CSS 4** for styling
- **Zustand** for state management
- **React Router** for navigation
- **Lucide React** for icons
- **Axios** for API communication

### Safety & Governance
- Content filtering with pattern matching
- Policy enforcement engine
- Tamper-proof audit logging with chain-of-custody
- Rate limiting and quota management
- Human-in-the-loop approval gates
- Cost tracking and limits

### Monitoring
- Prometheus metrics collection
- Grafana dashboards
- Structured JSON logging
- OpenTelemetry instrumentation

## Quick Start

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your NVIDIA_API_KEY

# Run development server
python run.py
```

### Frontend Setup

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
```

## API Endpoints

### Chat
- `POST /api/chat` - Stream chat with multi-agent processing
- `POST /api/chat/simple` - Non-streaming chat

### Workflows
- `POST /api/research` - Deep research workflow
- `POST /api/code` - Code generation workflow
- `POST /api/browse` - Browser automation workflow

### System
- `GET /api/health` - Health check
- `GET /api/status` - System status
- `GET /api/agents` - Agent pool status
- `GET /api/metrics` - System metrics

### Management
- `POST /api/upload` - File upload
- `GET /api/memory` - Memory query
- `GET /api/hierarchy` - Agent hierarchy
- `POST /api/plan` - Create execution plan

## Configuration

Key environment variables:

```
ENVIRONMENT=production
NVIDIA_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/leonore
REDIS_URL=redis://localhost:6379/0
VECTOR_DB_TYPE=milvus
ENABLE_CONTENT_FILTER=true
ENABLE_AUDIT_LOGGING=true
COMPLIANCE_MODE=false
```

## Workflows

### Deep Research
Multi-step research with web scraping, PDF parsing, and RAG-based retrieval.

### Code Generation
Test-first code generation with iterative refinement and sandboxed execution.

### Browser Automation
Intelligent web automation with natural language planning and execution.

## Safety Features

- **Content Filtering**: Blocks malware, illegal, privacy-violating, and abusive content
- **Policy Engine**: Enforces action restrictions and approval requirements
- **Audit Trail**: Immutable chain-of-custody logging for all operations
- **Rate Limiting**: Per-user request throttling
- **Quota Management**: Monthly cost limits per user
- **Human Approval**: Optional approval gates for high-risk actions

## Development

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

### Testing
```bash
pytest tests/ -v
```

## Deployment

### Docker
```bash
docker build -t leonore:latest .
docker run -p 8000:8000 leonore:latest
```

### Docker Compose
```bash
docker-compose up --build
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  Dashboard | Chat | Agents | Workflows | Analytics          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Gateway                             │
│  Auth | Rate Limit | Metrics | Error Handling               │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼────────┐
│ Orchestrator │  │ Safety Mgr  │  │ Audit Log   │
│ Multi-Agent  │  │ Policies    │  │ Chain-of-   │
│ Coordinator  │  │ Filtering   │  │ Custody     │
└───────┬──────┘  └──────┬──────┘  └────┬────────┘
        │                │              │
        └────────────────┼──────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼────────┐
│ NVIDIA NIM   │  │ Vector DB   │  │ Redis/      │
│ LLM Inference│  │ (Milvus)    │  │ Celery      │
└──────────────┘  └─────────────┘  └─────────────┘
```

## Performance

- **Latency**: <300ms token generation (RTX 4090)
- **Throughput**: 100+ concurrent requests
- **Memory**: Efficient agent pooling with auto-scaling
- **Cost**: Tracked per-user with monthly limits

## Security

- JWT authentication with configurable expiration
- API key management with hashing
- HTTPS/TLS support
- CORS configuration
- Input validation and sanitization
- SQL injection prevention via ORM

## Monitoring

Access Prometheus metrics at `/metrics` and Grafana dashboards at `http://localhost:3000`.

## License

MIT
