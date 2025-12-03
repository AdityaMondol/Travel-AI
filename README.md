# Manus Agent Platform

A production-grade, local-first autonomous multi-agent system inspired by Manus.
Built with Python (FastAPI) and React (TailwindCSS 4.0).
Powered by NVIDIA NIM for inference.

## Architecture

```ascii
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  Submission | Plan Inspector | Live Logs | Artifact View    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Gateway                             │
│  /jobs | /stream | /artifacts | /audit                      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼────────┐
│ Orchestrator │  │ Safety Mgr  │  │ Audit Log   │
│ (Planner)    │  │ Policy/PII  │  │ SQLite      │
└───────┬──────┘  └──────┬──────┘  └────┬────────┘
        │                │              │
        ▼                ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Pool                             │
│  [Researcher] [Coder] [PPT] [Browser] [Verifier]            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  NVIDIA NIM Client                          │
│  LLM (Llama3) | Embed (NV-Embed) | Image Gen (SDXL)         │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Agent Orchestration**: Hierarchical planning with specialized agents.
- **Deep Research**: Web scraping, RAG (FAISS), and citation-backed reporting.
- **Code Generation**: TDD-based synthesis with local sandbox execution.
- **Artifacts**: Auto-generated PPTX slides, code bundles, and reports.
- **Safety First**: Pre-flight intent validation, PII scanning, and immutable audit logs.
- **Local Execution**: No Docker required. Runs in standard Python/Node environments.

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA NIM API Key

### Backend (Python)

1. Navigate to the root directory.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Set your NVIDIA API Key:
   ```bash
   # Windows (PowerShell)
   $env:NVIDIA_API_KEY="your_key_here"
   # Linux/Mac
   export NVIDIA_API_KEY="your_key_here"
   ```
4. Run the server:
   ```bash
   python -m backend.main
   ```
   Server runs at `http://localhost:8000`.

### Frontend (React)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`.

## Usage

1. Open the frontend URL.
2. Enter a high-level objective (e.g., "Research quantum computing and create a slide deck").
3. Watch the **Planner** decompose the task.
4. Observe agents (Researcher, Coder, PPT) executing in parallel.
5. Review generated artifacts and audit logs.

## Safety & Governance

- **Intent Validation**: Every job is screened for illegal/harmful intent before execution.
- **Domain Allowlist**: Browser agent is restricted to safe domains (configurable).
- **Audit Log**: All actions are recorded in `manus.db` and visible in the UI.
- **Human-in-the-Loop**: Critical actions (like external API calls) can be configured to require approval.

## Agents

- **Planner**: Decomposes goals into dependency-aware plans.
- **Researcher**: Scrapes web content, embeds into RAG, and synthesizes reports.
- **Coder**: Writes Python code, generates tests, and executes in a local sandbox.
- **PPT**: Generates PowerPoint presentations using `python-pptx`.
- **Browser**: Controls a headless browser for specific automation tasks.
- **Verifier**: Audits outputs for factual accuracy and safety compliance.

## License

MIT
