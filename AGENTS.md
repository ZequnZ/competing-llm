# Project Overview

This project is for building an LLM chat application that pushes multiple LLMs competing with each other to provide the best responses to user queries.

## Backend
Backend is developed via Python, and FastAPI is used to build the API server for the application.

## Frontend
Frontend is developed via React with [Shadcn-UI](https://ui.shadcn.com/) and TypeScript.
Features include:
- **Modern Chat Interface**: Clean, responsive design with conversation management
- **Conversation History**: Sidebar with conversation threads and management
- **Real-time Messaging**: Interactive chat with AI assistant
- **Mobile Responsive**: Optimized for both desktop and mobile devices

Check out this [llms.txt](https://ui.shadcn.com/llms.txt) file for more details.

## Development rules

1. **Package management**: ONLY use `uv`, NEVER `pip`
2. **Python package imports**: ONLY use absolute imports for all imports.
2. **Branching**: NEVER work on `main`, always create feature branches
3. **Type safety**: All functions require type hints
4. **Testing**: New features need tests, bug fixes need regression tests
5. **Commits**: Use trailers for attribution, never mention tools/AI

## Configuration management

- Read [configuration](./competing-llm/backend/configuration/config_settings.py) script to understand how configuration is managed
- Environment-specific configs in `pyproject.toml` under `[config.<env>]`
- Required environment variable: `ENVIRONMENT` (e.g., "local", "dev", "prod")
- Configuration priority order:
  1. CLI arguments
  2. Environment-specific pyproject.toml table
  3. Default pyproject.toml table
  4. Environment variables

### Dependencies:
- Add runtime dependencies with: `uv add package-name`
- Add dev dependencies with: `uv add --group dev package-name`
- Keep dependencies minimal and well-justified
- Pin major versions for stability
