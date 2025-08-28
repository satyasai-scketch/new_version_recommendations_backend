from api.flask_app import create_app
from config.settings import Settings
from api.middleware import configure_logging
from api.errors import register_error_handlers

def create_validated_app():
    # Validate critical config at boot (fail fast)
    s = Settings()
    assert s.openai_api_key, "OPENAI_API_KEY is required"
    assert s.llm_model, "LLM model is required"

    app = create_app()
    configure_logging(app)
    register_error_handlers(app)
    return app

app = create_validated_app()

if __name__ == "__main__":
    # For local dev; in prod use gunicorn/uwsgi
    app.run(host="0.0.0.0", port=8000)
