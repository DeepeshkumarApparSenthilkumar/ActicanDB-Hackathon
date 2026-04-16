# RepoMind

Ask plain-English questions about any codebase. Get cited answers with file paths and line numbers — fully local, no cloud required.

Built for the **Actian VectorAI DB Build Challenge** · April 2026

---

## How It Works

```
Ingest: file walk → AST chunk (tree-sitter) → embed (Ollama) → vector store (chromadb)
Query:  embed question → vector search → Claude API → SSE stream → React UI
```

## Prerequisites

- Python 3.11+
- Node 20+
- [Ollama](https://ollama.ai) running locally with `nomic-embed-text`:
  ```bash
  ollama pull nomic-embed-text
  ```
- Anthropic API key (for Claude answers)

## Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY=your_key

# Frontend
cd ../frontend
npm install
```

## Run

```bash
./start.sh
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Offline Mode

```bash
OFFLINE_MODE=true ./start.sh
```

Uses Ollama for embeddings (always local). Set `LLM_MODEL` to an Ollama model for fully offline LLM too.

## Usage

1. Open http://localhost:5173
2. Enter a local repo path in the left panel → click **Index**
3. Ask questions in the center chat panel
4. Source code excerpts appear in the right panel with file + line citations

## Architecture

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Vector store | chromadb (local, persistent) |
| Embeddings | nomic-embed-text via Ollama |
| LLM | Claude claude-sonnet-4-6 (Anthropic API) |
| Chunking | tree-sitter (AST-aware) + sliding window fallback |
| Frontend | React 19 + Vite + TypeScript |

## Supported Languages

Python, TypeScript, JavaScript, Go, Rust, Java, C++, C, Markdown

## Running Tests

```bash
cd backend
python -m pytest ../tests/ -v
```

## Note on VectorAI DB

The hackathon spec calls for Actian VectorAI DB. During development, the Python SDK was not available on PyPI. The vector store layer (`backend/db/vectorai.py`) uses **chromadb** as a drop-in — same interface, same local-file persistence model, same cosine similarity search. Swapping to the official Actian SDK requires editing only that one file.
