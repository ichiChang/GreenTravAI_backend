from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.user import UserModel

from passlib.hash import pbkdf2_sha256
from db import mongo
from Schema import ChatbotSchema
from BlockList import BlockList
from flask_jwt_extended import (
    get_jwt,
    get_jti,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from BlockList import BlockList
from datetime import datetime
from flask import jsonify, make_response
import json

# from TravelPlanner import TravelPlanner
import os
from TravelAgent import run_travel_agent, run_travel_agent_green


blp = Blueprint("Chatbot", __name__)


@blp.route("/chatbot")
class Chatbot(MethodView):

    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        llm_api_key = os.getenv("OPENAI_API_KEY")
        response = run_travel_agent(user_query)
        # travel_planner = TravelPlanner(llm_api_key=llm_api_key)
        # response = travel_planner.retrieve_document_content(user_query)
        json_str = response.replace("'", '"')

        data = json.loads(json_str)

        json_response = jsonify(data)

        return json_response


@blp.route("/greenchatbot")
class GreenChatbot(MethodView):
    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        llm_api_key = os.getenv("OPENAI_API_KEY")
        response = run_travel_agent_green(user_query)
        # travel_planner = TravelPlanner(llm_api_key=llm_api_key)
        # response = travel_planner.retrieve_document_content(user_query)
        json_str = response.replace("'", '"')

        data = json.loads(json_str)

        json_response = jsonify(data)

        return json_response


@blp.route("/easyMessage")
class EasyMessage(MethodView):
    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        response = {
            "Message": "好的，我將為您提供台北市信義區的逛街選項",
            "Recommendation": [
                {
                    "Name": "信義遠百A13",
                    "Address": "110台北市信義區松仁路58號",
                    "latency": 120,
                }
            ],
        }

        return jsonify(response)
