from flask import Flask
from infra.factory import build_recommendation_controller
from controllers.recommendation_controller import RecommendationController
from .routes import register_routes

def create_app() -> Flask:
    app = Flask(__name__)
    controller: RecommendationController = build_recommendation_controller()
    register_routes(app, controller)
    return app
