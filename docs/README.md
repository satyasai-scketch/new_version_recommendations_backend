# New Version Recommendations Backend

## Overview
This project is a **Flask-based backend service** that delivers AI-powered product recommendations.
It is structured with clean layers, dependency injection, and type-safe boundaries to ensure maintainability, scalability, and testability.

## Features
- **Recommendation API**: Provides personalized product recommendations and complementary product suggestions.
- **AI Integration**: Uses LangChain's `ChatOpenAI` for LLM calls and embedding models.
- **Vector Search**: Supports multiple vector store backends (e.g., FAISS, Pinecone).
- **Profile Management**: Extracts and manages customer profiles from text data.
- **Health Checks**: `/healthz` endpoint to validate environment and configuration.
- **Robust Logging**: Request ID propagation, duration metrics, and safe header logging.
- **Error Handling**: Centralized error middleware with JSON responses.
- **Configuration**: Environment-driven configuration via Pydantic `Settings`.

## Project Structure
```
new_version_recommendations_backend/
│
├── api/                   # Flask API routes, middleware, error handlers
│   ├── routes.py
│   ├── middleware.py
│   ├── error_handlers.py
│   └── health.py
│
├── config/                # Settings and configuration
│   └── settings.py
│
├── controllers/           # Request/response orchestration layer
│   └── recommendation_controller.py
│
├── services/              # Business logic
│   └── recommender_service.py
│
├── data/                  # Data access, repositories, external APIs
│   └── profile_repository.py
│
├── llm/                   # LLM & embedding clients, prompts, parsers
│   ├── clients/
│   │   ├── openai_chat.py
│   │   └── openai_embeddings.py
│   ├── parsers.py
│   ├── prompts.py
│   └── interfaces.py
│
├── vectorstores/          # Vector database abstractions
│   ├── base.py
│   └── faiss_store.py
│
├── infra/                 # Composition root, dependency injection factory
│   └── factory.py
│
├── main.py                # Application entrypoint (creates Flask app)
│
├── deploy/
│   └── gunicorn.conf.py   # Production deployment configuration
│
└── docs/
    └── README_TEN_OUT_OF_TEN.md  # Enhancement notes
```

## Key Design Principles
- **Layered Architecture**: Clear separation of concerns between API, controllers, services, data, and infra.
- **Dependency Inversion**: LLM, embeddings, and vector store clients are injected via protocols/interfaces.
- **Pydantic Models**: Used for schema validation, configuration, and LLM I/O.
- **12-Factor Ready**: Config driven by environment variables.
- **Resilience**: Centralized error handling, safe logging, health checks.

## API Endpoints
### Health
- `GET /healthz` → Returns status, environment, and model info.

### Recommendations
- `GET /recommendations?customer_id=123`
  - Returns product recommendations and complementary suggestions for a customer.

## Configuration
Environment variables (loaded by `config/settings.py`):
- `OPENAI_API_KEY` – API key for LLM
- `LLM_MODEL` – LLM model name
- `EMBEDDINGS_MODEL` – Embeddings model name
- `VECTORSTORE_PROVIDER` – Which vectorstore backend to use (`faiss`, `pinecone`, etc.)
- `ENVIRONMENT` – `dev`, `staging`, `prod`

## Logging & Monitoring
- Logs every request with:
  - `request_id`, duration, method, path, status code
  - query/body sizes, masked sensitive headers
- Propagates `X-Request-ID` header

## Deployment
Run locally:
```bash
export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=8000
```

Run with Gunicorn:
```bash
gunicorn -c deploy/gunicorn.conf.py
```

## Testing
- Unit tests (using pytest) recommended for each layer:
  - Controllers (Flask test client)
  - Services (mocked dependencies)
  - LLM parsers (sample LLM responses)

## Future Enhancements
- OpenAPI spec generation (possible migration to FastAPI).
- Background jobs for profile enrichment.
- Real-time streaming responses from LLM.
- Rate limiting / API key authentication for production.
