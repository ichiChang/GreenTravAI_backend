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
import json
from TravelAgent import run_travel_agent, run_travel_agent_green


blp = Blueprint("Chatbot", __name__)


@blp.route("/chatbot")
class Chatbot(MethodView):

    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        # Initialize the response format
        res_format = {
            "response": {"Text_ans": None, "results": [], "Recommendation": []}
        }
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        llm_api_key = os.getenv("OPENAI_API_KEY")
        response = run_travel_agent(user_query)
        # print(response)

        if isinstance(response, str):
            res_format["response"]["Text_ans"] = response
        if isinstance(response, list) and len(response) > 0:
            if "results" in response[0]:
                res_format["response"]["results"] = response["results"]
            if "Recommendation" in response[0]:
                res_format["response"]["Recommendation"] = response

        else:
            if "results" in response:
                res_format["response"]["results"] = response["results"]

            if "Recommendation" in response:
                res_format["response"]["Recommendation"] = response["Recommendation"]

        return jsonify(res_format)


@blp.route("/greenchatbot")
class GreenChatbot(MethodView):
    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        res_format = {
            "response": {"Text_ans": None, "results": [], "Recommendation": []}
        }
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        llm_api_key = os.getenv("OPENAI_API_KEY")
        response = run_travel_agent_green(user_query)
        if isinstance(response, str):
            res_format["response"]["Text_ans"] = response
        if isinstance(response, list) and len(response) > 0:
            if "results" in response[0]:
                res_format["response"]["results"] = response["results"]
            if "Recommendation" in response[0]:
                res_format["response"]["Recommendation"] = response

        else:
            if "results" in response:
                res_format["response"]["results"] = response["results"]

            if "Recommendation" in response:
                res_format["response"]["Recommendation"] = response["Recommendation"]

        return jsonify(res_format)


@blp.route("/easyMessage")
class EasyMessage(MethodView):
    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        if "逛街" in user_query:
            response = {
                "Message": "我會建議你去 **台北 101 購物中心**。  這裡不僅是台北市的地標，購物選擇也非常多樣化，從奢侈品牌到特色餐飲應有盡有。購物完還可以登上 101 大樓的觀景台，俯瞰整個台北市，尤其是傍晚時分可以欣賞到日落和城市夜景，非常值得一逛。  ",
                "Recommendation": [
                    {
                        "Name": "信義遠百A13",
                        "Address": "110台北市信義區松仁路58號",
                        "Latency": 120,
                    }
                ],
            }
        elif "住宿" in user_query:
            hotel_recommendations = """
        # 台北市熱門飯店推薦 (2024年10月20日至10月23日)

        以下是符合您入住人數和預算範圍（1500~5000 TWD）的飯店推薦：

        1. **台北北門世民酒店 (CitizenM Taipei North Gate)**
        - **價格**：約3800 TWD
        - **評價**：8.8
        - **特色**：現代設計、便利的交通，靠近台北車站。
        - [預訂連結](https://www.citizenm.com)

        2. **君品酒店 (Palais de Chine Hotel)**
        - **價格**：約5000 TWD
        - **評價**：8.7
        - **特色**：結合法國浪漫和台灣文化的豪華住宿。
        - [預訂連結](https://www.palaisdechinehotel.com)

        3. **捷絲旅台北西門館 (Just Sleep Taipei Ximen)**
        - **價格**：約2600 TWD
        - **評價**：8.7
        - **特色**：提供舒適的住宿，位置便利，靠近西門町。
        - [預訂連結](https://www.justsleephotels.com)

        4. **金普頓大安酒店 (Kimpton DaAn Hotel Taipei)**
        - **價格**：約5700 TWD
        - **評價**：8.4
        - **特色**：獨特設計、優質服務，接近大安森林公園。
        - [預訂連結](https://www.ihg.com)

        這些飯店都擁有良好的評價和便利的地理位置，適合您在台北的住宿需求。希望您有個愉快的旅程！
        """
            response = {
                "Message": hotel_recommendations,
                "Recommendation": [],
            }

        return jsonify(response)


@blp.route("/easyGreenMessage")
class EasyGreenMessage(MethodView):
    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        if "逛街" in user_query:
            response = {
                "Message": "我會建議你去 **台北 101 購物中心**。  這裡不僅是台北市的地標，購物選擇也非常多樣化，從奢侈品牌到特色餐飲應有盡有。購物完還可以登上 101 大樓的觀景台，俯瞰整個台北市，尤其是傍晚時分可以欣賞到日落和城市夜景，非常值得一逛。  ",
                "Recommendation": [
                    {
                        "Name": "信義遠百A13",
                        "Address": "110台北市信義區松仁路58號",
                        "Latency": 120,
                    }
                ],
            }
        elif "住宿" in user_query:
            green_hotel_recommendations = """
            # 台北市環保旅館推薦 (2024年10月20日至10月23日)

            以下是幾家適合您需求的環保或綠色旅館：

            1. **台北凱達大飯店**  
            獲得「金級環保旅館」認證，提供綠色設施與服務。  
            [訂房連結](https://www.caesarmetro.com.tw)

            2. **台北圓環國際青年旅舍**  
            綠色認證旅館，注重可持續發展和社會責任，適合預算旅客。  
            [訂房連結](https://www.youthhostel.com.tw)

            3. **台北綠意飯店**  
            提供環保的住宿選擇，並致力於減少環境影響。  
            [訂房連結](https://www.greenhotel.com.tw)

            這些住宿選擇都符合環保標準，並提供良好的服務。希望您能找到合適的住宿！
            """
            response = {
                "Message": green_hotel_recommendations,
                "Recommendation": [],
            }

        return jsonify(response)
