# Competing LLM Backend

This is the FastAPI backend for the competing LLM chat application.

## Quick Start

### Run the Backend
```bash
# Set environment
export ENVIRONMENT=local

# Run the server
uv run python -m competing_llm.backend.app
```

### Run Tests
```bash
# Run all tests
uv run pytest competing-llm/backend/tests/

# Run specific test file
uv run pytest competing-llm/backend/tests/test_llm_mock.py

# Run with coverage
uv run pytest competing-llm/backend/tests/ --cov=competing-llm/backend/
```

### API Endpoints

- **POST /api/chat/stream** - Stream from single LLM
- **POST /api/chat/stream/batch** - Stream from multiple LLMs
- **GET /api/chat/health** - Health check
- **GET /api/chat/llms** - List available LLMs

### Example Usage

```bash
# Test single LLM streaming
curl -N http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hello world", "llm_id": 1}'

# Test multi-LLM streaming
curl -N http://localhost:8000/api/chat/stream/batch \
  -H "Content-Type: application/json" \
  -d '{"prompt": "explain AI", "llm_ids": [1, 2, 3]}'
```
