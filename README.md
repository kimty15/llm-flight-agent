# Nha Trang Trip Planner Agent

Backend agent for planning trips in Nha Trang, Vietnam.

It uses:

- FastAPI for the API
- LangGraph for a controlled workflow
- FAISS RAG for local Nha Trang knowledge
- SerpAPI for meal-stop search
- LangGraph `MemorySaver` for per-session memory
- Guardrails for input safety
- Langfuse v2 for optional tracing

## Flow

```text
User
  -> FastAPI /api/v1/chat
  -> Guardrails
  -> LangGraph
     -> analyze_request
     -> retrieve_knowledge
     -> search_food_if_needed
     -> generate_response
  -> Response
```

## Key Files

| Path | Purpose |
| --- | --- |
| `app.py` | FastAPI app and chat endpoint |
| `core/agent_factory.py` | Builds the LangGraph workflow |
| `core/nodes.py` | Workflow node logic |
| `core/state.py` | Graph state |
| `agents/retrieval/` | FAISS retrieval |
| `agents/food_agent/` | SerpAPI food search |
| `prompts/prompt_template.py` | Agent prompts |
| `safety/guardrails.py` | Input guardrails |
| `observability/langfuse_setup.py` | Langfuse callback setup |
| `docker-compose.yml` | API + Langfuse v2 + Postgres |

## Environment

Create `.env`:

```bash
copy .env.example .env
```

Required values:

```dotenv
OPENAI_API_KEY=...
SERPAPI_API_KEY=...
SAVE_PATH=faiss_index_openai_embeddings
```

Optional Langfuse values, after creating a project in Langfuse:

```dotenv
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

CLI:

```bash
python -m core.graph
```

## Run With Docker

```bash
copy .env.example .env
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Langfuse v2: `http://localhost:3000`
- Postgres: internal Langfuse database

Stop:

```bash
docker compose down
```

For background mode:

```bash
docker compose up --build -d
```

## Langfuse v2

1. Start Docker Compose.
2. Open `http://localhost:3000`.
3. Create an account and project.
4. Copy project keys into `.env`.
5. Restart the app:

```bash
docker compose restart app
```

Inside Docker Compose, the app uses:

```dotenv
LANGFUSE_HOST=http://langfuse-server:3000
```

Useful trace metadata:

- `session_id`
- `user_id`
- `request_id`
- graph node calls
- LLM calls
- guardrail flags

## API

| Method | Path |
| --- | --- |
| `GET` | `/health` |
| `POST` | `/api/v1/chat` |

Example:

```json
{
  "message": "Plan 2 days in Nha Trang for a couple",
  "session_id": "demo-1",
  "user_id": "user-123"
}
```

Response includes:

- `response`
- `session_id`
- `messages`
- `request_id`
- `guardrail_flags`

## Notes

- Memory is per `session_id` and is not durable after app restart.
- FAISS index is mounted into Docker at `./faiss_index_openai_embeddings`.
- Langfuse v2 secrets in `.env` should be changed before deployment.
- Live OpenAI, SerpAPI, and Langfuse behavior requires valid keys.

## Tests

```bash
python -m pytest
```
