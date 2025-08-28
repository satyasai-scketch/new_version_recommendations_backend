# app/controller/recommendation_controller.py
from flask import jsonify, request
from service.recommender_service import RecommenderService

class RecommendationController:
    def __init__(self, service: RecommenderService):
        self.service = service

    def get_recommendations(self):
        id_param = request.args.get("id")
        if id_param is None or not id_param.isdigit():
            return jsonify({"error": "id (int) is required"}), 400
        result = self.service.get_recommendations(customer_id=str(id_param))
        return jsonify(result.model_dump()), 200
