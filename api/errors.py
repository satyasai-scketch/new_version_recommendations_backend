# new_version_recommendations_backend/api/errors.py
import logging
from werkzeug.exceptions import HTTPException
from flask import jsonify, request, g

log = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def _handle_http_error(err: HTTPException):
        payload = {
            "code": err.code,
            "error": err.name,
            "message": err.description,
            "path": request.path,
            "request_id": getattr(g, "request_id", None),
        }
        # warn for 4xx, error for 5xx
        (log.warning if 400 <= err.code < 500 else log.error)(payload)
        return jsonify(payload), err.code

    @app.errorhandler(Exception)
    def _handle_unexpected_error(err: Exception):
        # Do not leak internal details
        log.exception({"event": "unhandled_exception", "path": request.path, "request_id": getattr(g, "request_id", None)})
        payload = {
            "code": 500,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "path": request.path,
            "request_id": getattr(g, "request_id", None),
        }
        return jsonify(payload), 500
