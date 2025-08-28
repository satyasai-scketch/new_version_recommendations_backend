wsgi_app = "new_version_recommendations_backend.main:app"
bind = "0.0.0.0:8000"
workers = 2
threads = 4
timeout = 120
graceful_timeout = 30
# accesslog = "-"  # stdout
# errorlog = "-"   # stdout
