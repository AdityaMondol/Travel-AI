# Leonore AI

Ultra-performant Multi-Agent AI Assistant System powered by NVIDIA NIM APIs

## Features

### Core Architecture
- **Hierarchical Multi-Agent System**: Unlimited recursive agent spawning with automatic promotion/demotion
- **Autonomous Planning**: Multi-step plan generation with parallel execution and adaptive replanning
- **Dynamic Tool Creation**: AI-generated tools created on-demand from natural language descriptions
- **Long-Term Memory**: Vector + Graph stores with infinite context via smart summarization
- **Real-time Reflection**: Self-criticism loops with continuous performance optimization

### Agent Capabilities
- **Specialist Agents**: Coder, Researcher, Analyst, Strategist, Designer with recursive sub-team spawning
- **Computer Use**: Full OS control (mouse, keyboard, screenshots, OCR) via NVIDIA Vision models
- **Code Execution**: Python, JavaScript, Bash, PowerShell with sandboxed execution
- **Web Automation**: Selenium-based browser control with intelligent navigation
- **File Operations**: Complete workspace management with async I/O

### Advanced Features
- **Overdrive Mode**: Unrestricted agent operation with maximum capability
- **Genesis Protocol**: Hidden backdoor for full system unlock (authorization required)
- **Parallel Tool Execution**: Concurrent task processing across agent hierarchy
- **Sub-300ms Latency**: Optimized for NVIDIA NIM inference with RTX 4090 support

### Frontend
- **Real-time Streaming**: Server-sent events with live agent thought visualization
- **Modern UI**: TailwindCSS, dark/light mode, draggable panels
- **Voice I/O**: Speech recognition and synthesis
- **File Upload**: Multi-file analysis with drag-drop
- **Markdown + LaTeX**: Full rendering support

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Add NVIDIA_API_KEY
python run.py
```

Open http://localhost:8000

## Docker Deployment

```bash
docker-compose up --build
```

## API Endpoints

### Core
- `POST /api/chat` - Stream chat with multi-agent processing
- `POST /api/upload` - File upload and analysis
- `GET /api/agents` - Agent pool status
- `GET /api/memory` - Memory query

### Workflows (LangGraph)
- `POST /api/research` - Deep research with web scraping
- `POST /api/code` - Fullstack code generation
- `POST /api/browse` - Browser interaction automation

### Advanced
- `POST /api/overdrive` - Activate unrestricted mode
- `POST /api/plan` - Create autonomous execution plan
- `POST /api/tools/create` - Generate dynamic tool
- `GET /api/hierarchy` - Agent hierarchy stats

### Chat Commands
- `research: <query>` - Trigger deep research workflow
- `code: <task>` - Trigger fullstack coding workflow
- `browse: <goal>` - Trigger browser interaction workflow

## NVIDIA NIM Models (25+)

- **Llama 3.1**: 405B, 70B, 8B
- **Llama 3.2 Vision**: 90B, 11B
- **Mistral**: Large 2, Nemo 12B
- **Mixtral**: 8x7B, 8x22B
- **Codestral**: 22B
- **Nemotron**: 4-340B, 70B
- **Granite**: 34B, 8B
- **DeepSeek Coder**: 33B
- **Qwen 2.5**: 72B, Coder 32B
- **Gemma 2**: 27B, 9B, 2B

## Architecture

```
app/
├── agents/
│   ├── base_agent.py           # Base agent with overdrive support
│   ├── orchestrator.py         # Multi-agent coordinator
│   ├── specialist_agent.py     # Domain specialists
│   ├── planner.py              # Autonomous planning
│   ├── hierarchy_manager.py    # Agent hierarchy control
│   └── reflection_engine.py    # Self-improvement loops
├── memory/
│   ├── vector_store.py         # Semantic memory
│   ├── graph_store.py          # Relational memory
│   └── long_term_memory.py     # Unified memory system
├── tools/
│   ├── code_executor.py        # Multi-language execution
│   ├── computer_use.py         # OS control
│   ├── web_browser.py          # Browser automation
│   ├── file_operations.py      # File management
│   ├── ocr_tool.py             # Vision + OCR
│   └── dynamic_tool_creator.py # AI tool generation
├── core/
│   ├── llm_client.py           # NVIDIA NIM client
│   ├── streaming.py            # SSE streaming
│   ├── context_manager.py      # Infinite context
│   ├── overdrive_mode.py       # Unrestricted operation
│   └── config.py               # Configuration
└── api/
    └── routes.py               # FastAPI endpoints
```

## Performance

- **Latency**: <300ms token generation (RTX 4090)
- **Context**: Infinite via smart summarization
- **Concurrency**: Unlimited parallel agent execution
- **Memory**: Persistent vector + graph stores

## License

MIT
