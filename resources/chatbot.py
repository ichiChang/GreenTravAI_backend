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
from TravelPlanner import check_and_extract_date
from TravelAgent import run_travel_agent, run_travel_agent_green
import datetime


blp = Blueprint("Chatbot", __name__)


@blp.route("/chatbot")
class Chatbot(MethodView):

    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        # Initialize the response format
        res_format = {
            "response": {"Text_ans": None, "results": [], "Plans": []}
        }
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        # llm_api_key = os.getenv("OPENAI_API_KEY")
        response = run_travel_agent(user_query)
        # print(response)

        if isinstance(response, str):
            res_format["response"]["Text_ans"] = response
        if isinstance(response, list) and len(response) > 0:
            if "results" in response[0]:
                res_format["response"]["results"] = response["results"]
            if "Recommendation" in response[0]:
                if "Recommendation" in response[0]:
                    final_note = ""
                    for recomm in response:
                        final_note += recomm['Note']
                        del recomm['Note']

                    res_format["response"]["Plans"] = response
                    res_format["response"]["Text_ans"] = final_note


        else:
            if "results" in response:
                res_format["response"]["results"] = response["results"]

            if "Recommendation" in response:
                res_format["response"]["Plans"] = response["Recommendation"]

        return jsonify(res_format)


@blp.route("/greenchatbot")
class GreenChatbot(MethodView):
    @blp.arguments(ChatbotSchema)
    @jwt_required()
    def post(self, user_data):
        res_format = {
            "response": {"Text_ans": None, "results": [], "Plans": []}
        }
        user_query = user_data["query"]

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        # llm_api_key = os.getenv("OPENAI_API_KEY")
        response = run_travel_agent_green(user_query)
        if isinstance(response, str):
            res_format["response"]["Text_ans"] = response
        if isinstance(response, list) and len(response) > 0:
            if "results" in response[0]:
                res_format["response"]["results"] = response["results"]
            if "Recommendation" in response[0]:
                if "Recommendation" in response[0]:
                    final_note = ""
                    for recomm in response:
                        final_note += recomm['Note']
                        del recomm['Note']

                    res_format["response"]["Plans"] = response
                    res_format["response"]["Text_ans"] = final_note


        else:
            if "results" in response:
                res_format["response"]["results"] = response["results"]

            if "Recommendation" in response:
                res_format["response"]["Plans"] = response["Recommendation"]

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
        # 台北市熱門飯店推薦 (2024年11月05日至11月07日)

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
            # 台北市環保旅館推薦 (2024年11月05日至11月07日)

            以下是幾家適合您需求的環保或綠色旅館：

            1. **D.G. Hotel**  
            台北D.G. Hotel以其現代設計和便捷的市中心位置而聞名，提供舒適的住宿體驗。這家酒店的評分為4.5，價格為**4275.0**，是想要探索台北市區的旅客的理想選擇
            [訂房連結](https://www.dghotel.com.tw/zh-tw)

            2. **台糖台北會館**  
            台糖台北會館位於市中心，提供舒適的住宿環境和便利的交通選擇。這裡的評價為4.0星，價格為**2727.0**。無論是商務旅行還是觀光旅遊，這裡都是理想的下榻之地 
            [訂房連結](http://www.taipeihotel-tsc.com.tw/)

            3. **圓山大飯店**  
            台北圓山大飯店以其獨特的中式宮殿建築風格和優雅的景觀而聞名，這裡的住宿體驗讓人感受到濃厚的文化氛圍和歷史底蘊。無論是來自世界各地的旅客還是本地的遊客，都能在這裡享受到高品質的服務和舒適的環境。飯店內部裝潢精緻，設施齊全，讓每位入住的客人都能感受到賓至如歸的感覺。這裡的餐飲選擇豐富多樣，無論是中式料理還是國際美食，都能滿足不同口味的需求。除此之外，飯店還提供多種休閒娛樂設施，讓客人在繁忙的都市生活中找到一片寧靜的天地。圓山大飯店不僅是一個住宿的地方，更是一個讓人流連忘返的旅遊勝地。價格為**3800.0**，這樣的價位對於這樣的住宿品質來說，絕對是物超所值
            [訂房連結](https://www.grand-hotel.org/)

            這些住宿選擇都符合環保標準，並提供良好的服務。希望您能找到合適的住宿！
            """
            response = {
                "Message": green_hotel_recommendations,
                "Recommendation": [],
            }
        
        elif "兩天一夜" in user_query:
            green_plan_recommendation ="""
            ### Day 1 Recommendations

            1. 早餐  
            **地址:** 臺北市松山區敦化北路222巷11號  
            **簡介* 提供多樣化的早餐選擇，適合開始一天的活力餐點。  
            **地點名稱:** 麥味登北市敦北  
            **停留時間:** 1 小時

            2. 景點參觀  
            **地址:** 臺北市大安區芳蘭路51號  
            **簡介:** 享受自然風光，探索多樣的植物園藝。  
            **地點名稱:** 臺大農場園藝分場  
            **停留時間:** 2 小時

            3. 午餐  
            **地址:** 臺北市大安區忠孝東路四段45號12樓  
            **簡介:** 提供泰式風味的餐點，環境優雅舒適。  
            **地點名稱:** Lady nara台北忠孝SOGO店  
            **停留時間:** 1 小時 30 分

            4. 景點參觀  
            **地址:** 臺北市士林區士商路189號  
            **簡介:** 適合親子同遊，探索科學的奧秘。  
            **地點名稱:** 國立臺灣科學教育館  
            **停留時間:** 2 小時 30 分

            5. 晚餐  
            **地址:** 臺北市大同區台北市大同區承德路1段1號4樓  
            **簡介:** 享受多樣的啤酒選擇和美味的餐點。  
            **地點名稱:** 金色三麥 台北京站店  
            **停留時間:** 1 小時 30 分

            6. 住宿  
            **地址:** 臺北市大同區承德路一段三號  
            **簡介:** 提供豪華舒適的住宿體驗，位於市中心，交通便利。  
            **地點名稱:** 台北君品大酒店  
            **停留時間:** 8 小時

            ---

            ### Day 2 Recommendations

            1. 早餐  
            **地址:** 臺北市大安區樂業街153號  
            **簡介:** 提供多樣化的早餐選擇，適合開始一天的活力餐點。  
            **地點名稱:** Q Burger大安樂業店  
            **停留時間:** 1 小時 

            2. 景點參觀  
            **地址:** 臺北市士林區雨聲街120號  
            **簡介:** 探索文化與生態的結合，享受綠意盎然的環境。  
            **地點名稱:** 芝山文化生態綠園  
            **停留時間:** 2 小時 

            3. 午餐  
            **地址:** 臺北市大安區仁愛路四段300巷9弄4號  
            **簡介:** 提供新鮮的壽司選擇，適合喜愛日式料理的旅客。  
            **地點名稱:** 美術系壽司(台北大安店)  
            **停留時間:** 1 小時 30 分

            4. 景點參觀  
            **地址:** 臺北市信義區福德街221巷12號  
            **簡介:** 了解環境教育的重要性，並參觀傳統廟宇。  
            **地點名稱:** 松山奉天宮環境教育中心  
            **停留時間:** 2 小時

            5. 晚餐  
            **地址:** 臺北市中山區敬業三路123號2樓  
            **簡介:** 享受旋轉壽司的樂趣，品嚐多樣化的壽司選擇。  
            **地點名稱:** 藏壽司 大直ATT店  
            **停留時間:** 1 小時 30 分
            ---

            ### Summary
            第一天的行程涵蓋了自然景觀與科學探索，並在市中心享用美食和舒適的住宿。第二天的行程以文化與生態探索為主，並享用日式料理，結束愉快的台北之旅。



"""
            response = {
                "Message": green_plan_recommendation,
                "Recommendation": [],
            }

        return jsonify(response)
