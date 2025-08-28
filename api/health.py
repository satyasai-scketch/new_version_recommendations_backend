from flask import Blueprint, jsonify
from config.settings import Settings

bp = Blueprint("health", __name__)

@bp.get("/healthz")
def healthz():
    """
    Lightweight health check endpoint.
    - Validates required config presence.
    - Optionally can ping vector store / embeddings in future.
    """
    s = Settings()
    status = {
        "status": "ok",
        "environment": s.environment,
        "llm_model": s.llm_model,
        "embeddings_model": s.embeddings_model,
        "vectorstore_provider": s.vectorstore_provider,
    }
    return jsonify(status), 200