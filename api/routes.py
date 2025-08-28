from flask import Flask
from controllers.recommendation_controller import RecommendationController
from .health import bp as health_bp

def register_routes(app: Flask, controller: RecommendationController):
    # Business endpoints
    app.add_url_rule(
        "/recommendations",
        view_func=controller.get_recommendations,
        methods=["GET"]
    )

    # Health endpoints
    app.register_blueprint(health_bp)
