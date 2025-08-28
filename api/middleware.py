import logging
import time
import uuid
from flask import g, request

REQUEST_ID_HEADER = "X-Request-ID"

SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}

def _safe_headers(headers):
    out = {}
    for k, v in headers.items():
        if k.lower() in SENSITIVE_HEADERS:
            out[k] = "***"
        else:
            out[k] = v
    return out

def configure_logging(app):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def _before_request():
        rid = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        g.request_id = rid
        g._start_time = time.time()

    @app.after_request
    def _after_request(response):
        duration_ms = int((time.time() - getattr(g, "_start_time", time.time())) * 1000)
        # Only sizes/metadata, avoid PII
        qs_len = len(request.query_string or b"")
        try:
            body_len = int(request.headers.get("Content-Length", "0"))
        except ValueError:
            body_len = 0

        payload = {
            "event": "request_complete",
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "request_id": getattr(g, "request_id", None),
            "client_ip": request.headers.get("X-Forwarded-For", request.remote_addr),
            "user_agent": request.headers.get("User-Agent"),
            "query_len": qs_len,
            "body_len": body_len,
            "headers": _safe_headers(request.headers),
        }
        app.logger.info(payload)
        response.headers[REQUEST_ID_HEADER] = getattr(g, "request_id", "")
        return response
