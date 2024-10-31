from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.user import UserModel
from models.travelPlan import TravelPlanModel
from models.day import DayModel
from models.stop import StopModel
from models.user import UserModel

from db import mongo
from Schema import (
    UserSchema,
    AddTravelPlanSchema,
    UpdateTravelPlanSchema,
    CreateAllSchema,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from datetime import datetime, timedelta
import os
from Route import (
    get_directions,
    get_duration_in_seconds,
    print_detailed_route_info,
    find_optimal_mode,
    get_lat_long,
)
from datetime import datetime, timedelta
from resources.stop import check_green



blp = Blueprint("TravelPlan", __name__, url_prefix="/travel_plans")


def calcarbon(distance, mode):
    # modes = ["driving", "walking", "bicycling", "transit", "TWO_WHEELER"]
    #  資料來原：行政院環保署碳排放計算器
    if mode is None:
        return 0
    emission_map = {
        "driving": 173,
        "walking": 0,
        "bicycling": 0,
        "transit": 4,
        "TWO_WHEELER": 46,
    }
    ans = round((emission_map.get(mode) or 0) * distance, 3)
    return ans


GREEEN_SPOT_REDUCTION_AMOUNT = 3000


@blp.route("/")
class TravelPlanList(MethodView):

    @blp.arguments(AddTravelPlanSchema)
    @jwt_required()
    def post(self, travel_plan_data):
        user_id = get_jwt_identity()
        user = UserModel.objects(id=user_id).first()
        if not user:
            abort(404, description="User not found")

        travel_plan = TravelPlanModel(
            planname=travel_plan_data["planname"],
            startdate=travel_plan_data["startdate"],
            enddate=travel_plan_data["enddate"],
            createAt=datetime.now(),
            userId=user.id,
        )
        travel_plan.save()

        current_date = travel_plan_data["startdate"]
        while current_date <= travel_plan_data["enddate"]:
            day = DayModel(
                Date=current_date,
                TravelPlanId=travel_plan.id,  # Associate the day with the travel plan
            )
            day.save()  # Save each DayModel instance to the database
            current_date += timedelta(days=1)
        data = jsonify(
            {
                "message": f'{user.username} created a travel plan named {travel_plan_data["planname"]}'
            }
        )
        return make_response(data, 201)

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.objects(id=user_id).first()
        if not user:
            abort(404, description="User not found")

        travel_plans = TravelPlanModel.objects(userId=user.id)
        data = jsonify(
            [
                {
                    "id": str(plan.id),
                    "planname": plan.planname,
                    "startdate": plan.startdate.strftime("%Y-%m-%d"),
                    "enddate": plan.enddate.strftime("%Y-%m-%d"),
                    "createdAt": plan.createAt,
                }
                for plan in travel_plans
            ]
        )
        return make_response(data, 200)


@blp.route("/<string:plan_id>")
class TravelPlanItem(MethodView):

    @jwt_required()
    def get(self, plan_id):
        user_id = get_jwt_identity()
        travel_plan = TravelPlanModel.objects(id=plan_id, userId=user_id).first()
        if not travel_plan:
            abort(404, description="Travel plan not found")
        data = jsonify(
            {
                "planname": travel_plan.planname,
                "startdate": travel_plan.startdate.strftime("%Y-%m-%d"),
                "enddate": travel_plan.enddate.strftime("%Y-%m-%d"),
                "createdAt": travel_plan.createAt,
            }
        )
        return make_response(data, 200)

    @blp.arguments(UpdateTravelPlanSchema)
    @jwt_required()
    def put(self, update_data, plan_id):
        user_id = get_jwt_identity()

        TravelPlanModel.objects(id=plan_id, userId=user_id).update(
            planname=update_data["Name"],
            startdate=update_data["StartDay"],
            enddate=update_data["EndDay"],
        )
        data = jsonify({"message": "Travel plan updated successfully"})
        return make_response(data, 200)

    @jwt_required()
    def delete(self, plan_id):
        user_id = get_jwt_identity()
        travel_plan = TravelPlanModel.objects(id=plan_id, userId=user_id).first()
        if not travel_plan:
            abort(404, description="Travel plan not found")
        travel_plan.delete()
        data = jsonify({"message": "Travel plan deleted successfully"})
        return make_response(data, 200)


@blp.route("/CreateAll")
class TravelPlanList(MethodView):

    @blp.arguments(CreateAllSchema)
    @jwt_required()
    def post(self, travel_plan_data):
        user_id = get_jwt_identity()
        user = UserModel.objects(id=user_id).first()
        actual_days = (
            travel_plan_data["enddate"] - travel_plan_data["startdate"]
        ).days + 1
        if actual_days != len(travel_plan_data["Plans"]):
            abort(
                400,
                description="travel plan phase and the plans of day is inconsistent",
            )

        if not user:
            abort(404, description="User not found")
        api_key = os.getenv("GOOGLE_MAP_API_KEY")
        travel_plan = TravelPlanModel(
            planname=travel_plan_data["planname"],
            startdate=travel_plan_data["startdate"],
            enddate=travel_plan_data["enddate"],
            createAt=datetime.now(),
            userId=user.id,
        )
        travel_plan.save()
        daynum = 0
        current_date = travel_plan_data["startdate"]
        while current_date <= travel_plan_data["enddate"]:
            day = DayModel(
                Date=current_date,
                TravelPlanId=travel_plan.id,  # Associate the day with the travel plan
            )
            day.save()  # Save each DayModel instance to the database
            # days --> Plans
            stopListInDay = travel_plan_data["Plans"][daynum]
            stop_num = 0
            # stops --> Recommendation
            for stop in stopListInDay["Recommendation"]:
                latency = stop["latency"]
                # current_stop = StopModel.objects()
                # place = PlaceModel.objects(id=stop_data["PlaceId"]).first()
                # day = DayModel.objects(id=stop["DayId"]).first()
                current_address = stop["Address"]
                if not day:
                    abort(404, description="Day not found")
                if stop_num > 0:
                    # prev_stop = StopModel.objects(id=stop["prev_stop"]).first()
                    prev_endtime = prev_stop.EndTime
                    prev_address = prev_stop.address

                    optimal_mode, duration, best_directions, best_distance_km = (
                        find_optimal_mode(prev_address, current_address, api_key)
                    )

                    # print(optimal_mode, duration)
                    long, lat = get_lat_long(current_address, api_key)
                    if optimal_mode:

                        starttime = prev_endtime + timedelta(minutes=int(duration / 60))
                        stp = StopModel(
                            Name=stop["Location"],
                            StartTime=starttime,
                            EndTime=starttime + timedelta(minutes=latency),
                            note=stop["Description"],
                            address=current_address,
                            transportation={},
                            # PlaceId=place.id,
                            DayId=day.id,
                            prev_stopId=str(prev_stop.id),
                            Isgreen=check_green(stop["Location"]),
                            coordinates=[long, lat],
                        )
                        stp.save()
                        prev_stop.transportation = {
                            "mode": optimal_mode,
                            "Timespent": int(duration / 60),
                            "distance": best_distance_km,
                            "LowCarbon": (
                                True
                                if optimal_mode not in ["driving", "TWO_WHEELER"]
                                else False
                            ),
                        }
                        prev_stop.save()
                        prev_stop = stp
                    #     transportation = TransportationModel(
                    # Name=optimal_mode,
                    # TimeSpent= int(duration/60),
                    # LowCarbon=True if optimal_mode != "driving" else False,
                    # FromStopId=prev_stop.id,
                    # ToStopId=stop.id,
                    #     )
                    #     transportation.save()

                    else:
                        abort(
                            500,
                            description=f"Fail to obtain the transportation between {prev_stop.Name} and {stop.Name}",
                        )

                else:
                    parsed_date = datetime.strptime(str(day.Date), "%Y-%m-%d")
                    new_date = parsed_date.replace(
                        hour=8, minute=0, second=0, microsecond=0
                    )
                    long, lat = get_lat_long(current_address, api_key)
                    # Convert back to string in yyyy-mm-dd hh:mm format
                    stp = StopModel(
                        Name=stop["Location"],
                        StartTime=new_date,
                        EndTime=new_date + timedelta(minutes=latency),
                        note=stop["Description"],
                        address=stop["Address"],
                        # PlaceId=place,
                        transportation={},
                        DayId=day,
                        Isgreen=check_green(stop["Location"]),
                        coordinates=[long, lat],
                    )
                    stp.save()
                    prev_stop = stp
                stop_num = stop_num + 1

            current_date += timedelta(days=1)
            daynum = daynum + 1

        data = jsonify({"message": f" Complete travelplan is created successfully"})
        return make_response(data, 201)


@blp.route("/CalCarbon")
class TravelPlanItem(MethodView):

    # @jwt_required()
    # def get(self):
    #     user_id = get_jwt_identity()
    #     user = UserModel.objects(id=user_id).first()
    #     if not user:
    #         abort(404, description="User not found")

    #     green_stats = user.green_stats
    #     if not green_stats:
    #         green_stats = {
    #             "emission_reduction": None,
    #             "green_trans_rate": None,
    #             "green_spot_rate": None,
    #         }
    #     data = jsonify(green_stats)
    #     return make_response(data, 200)

    # @blp.arguments(AddTravelPlanSchema)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.objects(id=user_id).first()
        if not user:
            abort(404, description="User not found")

        total_emission = 0
        total_distance = 0
        green_trans_point = 0
        total_trans_count = 0
        green_spot_coount = 0
        total_stop_count = 0
        plans = TravelPlanModel.objects(userId=user.id)

        for plan in plans:
            days = DayModel.objects(TravelPlanId=plan.id)
            for day in days:
                stops = StopModel.objects(DayId=day.id)
                total_stop_count += stops.count()
                for stop in stops:
                    # Get distance and mode with default values
                    if stop.Isgreen:
                        green_spot_coount += 1
                    if not (
                        stop.transportation.get("mode") is None
                        and stop.transportation.get("Timespent") is None
                        and stop.transportation.get("LowCarbon") is None
                    ):
                        total_trans_count += 1
                    distance = stop.transportation.get("distance") or 0
                    mode = (
                        stop.transportation.get("mode") or "unknown"
                    )  # You can set a default mode if needed
                    if mode in ["walking", "bicycling", "transit"]:
                        green_trans_point += 1

                    # print(stop.Name, calcarbon(distance, mode))
                    total_emission += calcarbon(distance, mode)
                    # print(total_emission)
                    total_distance += distance

        # Ensure you do not divide by zero
        if total_distance > 0:
            final_rate = (
                round((calcarbon(total_distance, "driving")) - total_emission, 2)
                # + green_spot_coount * GREEEN_SPOT_REDUCTION_AMOUNT
            )
        else:
            final_rate = 0  # Handle case where total_distance is 0
        if total_trans_count > 0:
            final_green_trans_rate = int(
                round((green_trans_point / total_trans_count), 2) * 100
            )
            # int((1 - round((emission/car_emission),2)) * 100)
        else:
            final_green_trans_rate = 0
        if total_stop_count > 0:
            final_green_spot_rate = int(
                round((green_spot_coount / total_stop_count), 2) * 100
            )
        else:
            final_green_spot_rate = 0

        green_stats = {
            "emission_reduction": final_rate,
            "green_trans_rate": final_green_trans_rate,
            "green_spot_rate": final_green_spot_rate,
        }
        user.green_stats = green_stats
        user.save()

        total_users = UserModel.objects.count()
        print(total_users)
        users_below = UserModel.objects.aggregate([
            {
                "$match": {
                    "$or": [
                        {"green_stats.emission_reduction": {"$lte": final_rate}}, 
                        {"green_stats.emission_reduction": {"$exists": False}}      
                    ]
                }
            },
            {"$count": "below_count"}
        ])
        users_below_count = list(users_below)
        below_count = users_below_count[0]["below_count"] if users_below_count else 0
        user_percentile = int((below_count / total_users) * 100) if total_users > 0 else 0


        data = jsonify(
            {
                "emission_reduction": final_rate,
                "green_trans_rate": final_green_trans_rate,
                "green_spot_rate": final_green_spot_rate,
                "green_percentile": user_percentile
            }
        )
        # data = jsonify({"message": "update green stats successfully"})

        return make_response(data, 200)


@blp.route("/CalCarbon/<string:plan_id>")
class TravelPlanItem_carbon(MethodView):

    # @jwt_required()
    # def get(self, plan_id):
    #     plan = TravelPlanModel.objects(id=plan_id).first()
    #     if not plan:
    #         abort(404, description="Travel plan not found")
        
    #     # Retrieve green_stats and set default values if fields are None
    #     green_stats = plan.green_stats or {}
    #     # print(plan.green_stats.get("emission_reduction"))
    #     # print(green_stats)
    #     emission_reduction = green_stats.get("emission_reduction", None)
    #     green_spot_rate = green_stats.get("green_spot_rate", None)
    #     green_trans_rate = green_stats.get("green_trans_rate", None)
        
    #     # print(emission_reduction)  # Should print 0 if emission_reduction is None
        
    #     # Populate green_stats with default values if needed
    #     green_stats = {
    #         "emission_reduction": emission_reduction,
    #         "green_trans_rate": green_trans_rate,
    #         "green_spot_rate": green_spot_rate,
    #     }
    #     # green_stats = plan.green_stats

        
    #     data = jsonify(green_stats)
    #     return make_response(data, 200)

    @jwt_required()
    def get(self, plan_id):
        # user_id = get_jwt_identity()
        plan = TravelPlanModel.objects(id=plan_id).first()
        if not plan:
            abort(404, description="Travel plan not found")

        total_emission = 0
        total_distance = 0
        green_trans_point = 0
        total_trans_count = 0
        green_spot_coount = 0
        total_stop_count = 0
        days = DayModel.objects(TravelPlanId=plan.id)
        for day in days:
            stops = StopModel.objects(DayId=day.id)
            total_stop_count += stops.count()
            for stop in stops:
                if stop.Isgreen:
                    green_spot_coount += 1
                # Get distance and mode with default values
                if not (
                    stop.transportation.get("mode") is None
                    and stop.transportation.get("Timespent") is None
                    and stop.transportation.get("LowCarbon") is None
                ):
                    total_trans_count += 1
                    # print(stop.transportation)
                distance = stop.transportation.get("distance") or 0
                mode = (
                    stop.transportation.get("mode") or "unknown"
                )  # You can set a default mode if needed
                if mode in ["walking", "bicycling", "transit"]:
                    green_trans_point += 1

                # print(stop.Name, calcarbon(distance, mode))
                total_emission += calcarbon(distance, mode)
                # print(total_emission)
                total_distance += distance

        # Ensure you do not divide by zero
        if total_distance > 0:
            final_rate = (
                round((calcarbon(total_distance, "driving")) - total_emission, 2)
                # + green_spot_coount * GREEEN_SPOT_REDUCTION_AMOUNT
            )
        else:
            final_rate = 0  # Handle case where total_distance is 0
        if total_trans_count > 0:
            final_green_trans_rate = int(
                round((green_trans_point / total_trans_count), 2) * 100
            )
        else:
            final_green_trans_rate = 0

        if total_stop_count > 0:
            final_green_spot_rate = int(
                round((green_spot_coount / total_stop_count), 2) * 100
            )
        else:
            final_green_spot_rate = 0
        green_stats = {
            "emission_reduction": final_rate,
            "green_trans_rate": final_green_trans_rate,
            "green_spot_rate": final_green_spot_rate,
        }
        plan.green_stats = green_stats
        print(plan.green_stats)
        plan.save()
        data = jsonify(
            {
                "emission_reduction": final_rate,
                "green_trans_rate": final_green_trans_rate,
                "green_spot_rate": final_green_spot_rate,
            }
        )
        # data = jsonify({"message": "update green stats successfully"})

        return make_response(data, 200)




@blp.route("/CreateAll_demo")
class TravelPlanList(MethodView):

    # @blp.arguments(CreateAllSchema)
    @jwt_required()
    def post(self):
        travel_plan_data = {
                    "startdate": "2024-11-20",
                    "enddate": "2024-11-21",
                    "planname": "台北兩天一夜(綠色)",
                    "Plans": [
                        {
                            "Recommendation": [
                                {
                                    "Activity": "早餐",
                                    "Address": "臺北市松山區敦化北路222巷11號",
                                    "Description": "提供多樣化的早餐選擇，適合開始一天的活力餐點。",
                                    "Location": "麥味登北市敦北",
                                    "latency": 60
                                },
                                {
                                    "Activity": "景點參觀",
                                    "Address": "臺北市大安區芳蘭路51號",
                                    "Description": "享受自然風光，探索多樣的植物園藝。",
                                    "Location": "臺大農場園藝分場",
                                    "latency": 120
                                },
                                {
                                    "Activity": "午餐",
                                    "Address": "臺北市大安區忠孝東路四段45號12樓",
                                    "Description": "提供泰式風味的餐點，環境優雅舒適。",
                                    "Location": "Lady nara台北忠孝SOGO店",
                                    "latency": 90
                                },
                                {
                                    "Activity": "景點參觀",
                                    "Address": "臺北市士林區士商路189號",
                                    "Description": "適合親子同遊，探索科學的奧秘。",
                                    "Location": "國立臺灣科學教育館",
                                    "latency": 150
                                },
                                {
                                    "Activity": "晚餐",
                                    "Address": "臺北市大同區台北市大同區承德路1段1號4樓",
                                    "Description": "享受多樣的啤酒選擇和美味的餐點。",
                                    "Location": "金色三麥 台北京站店",
                                    "latency": 90
                                },
                                {
                                    "Activity": "住宿",
                                    "Address": "臺北市大同區承德路一段三號",
                                    "Description": "提供豪華舒適的住宿體驗，位於市中心，交通便利。",
                                    "Location": "台北君品大酒店",
                                    "latency": 480
                                }
                            ]
                        },
                        {
                            "Recommendation": [
                                {
                                    "Activity": "早餐",
                                    "Address": "臺北市大安區樂業街153號",
                                    "Description": "提供多樣化的早餐選擇，適合開始一天的活力餐點。",
                                    "Location": "Q Burger大安樂業店",
                                    "latency": 60
                                },
                                {
                                    "Activity": "景點參觀",
                                    "Address": "臺北市士林區雨聲街120號",
                                    "Description": "探索文化與生態的結合，享受綠意盎然的環境。",
                                    "Location": "芝山文化生態綠園",
                                    "latency": 120
                                },
                                {
                                    "Activity": "午餐",
                                    "Address": "臺北市大安區仁愛路四段300巷9弄4號",
                                    "Description": "提供新鮮的壽司選擇，適合喜愛日式料理的旅客。",
                                    "Location": "美術系壽司(台北大安店)",
                                    "latency": 90
                                },
                                {
                                    "Activity": "景點參觀",
                                    "Address": "臺北市信義區福德街221巷12號",
                                    "Description": "了解環境教育的重要性，並參觀傳統廟宇。",
                                    "Location": "松山奉天宮環境教育中心",
                                    "latency": 120
                                },
                                {
                                    "Activity": "晚餐",
                                    "Address": "臺北市中山區敬業三路123號2樓",
                                    "Description": "享受旋轉壽司的樂趣，品嚐多樣化的壽司選擇。",
                                    "Location": "藏壽司 大直ATT店",
                                    "latency": 90
                                }
                            ]
                        }
                    ]
                }

        # user_id = get_jwt_identity()
        travel_plan_data["startdate"] = datetime.strptime(travel_plan_data["startdate"], "%Y-%m-%d")
        travel_plan_data["enddate"] = datetime.strptime(travel_plan_data["enddate"], "%Y-%m-%d")
        print('ok')
        user_id = '672330196b182d387e7a240a'
        user = UserModel.objects(id=user_id).first()
        actual_days = (
            travel_plan_data["enddate"] - travel_plan_data["startdate"]
        ).days + 1
        if actual_days != len(travel_plan_data["Plans"]):
            abort(
                400,
                description="travel plan phase and the plans of day is inconsistent",
            )

        if not user:
            abort(404, description="User not found")
        api_key = os.getenv("GOOGLE_MAP_API_KEY")
        travel_plan = TravelPlanModel(
            planname=travel_plan_data["planname"],
            startdate=travel_plan_data["startdate"],
            enddate=travel_plan_data["enddate"],
            createAt=datetime.now(),
            userId=user.id,
        )
        travel_plan.save()
        daynum = 0
        current_date = travel_plan_data["startdate"]
        while current_date <= travel_plan_data["enddate"]:
            day = DayModel(
                Date=current_date,
                TravelPlanId=travel_plan.id,  # Associate the day with the travel plan
            )
            day.save()  # Save each DayModel instance to the database
            # days --> Plans
            stopListInDay = travel_plan_data["Plans"][daynum]
            stop_num = 0
            # stops --> Recommendation
            for stop in stopListInDay["Recommendation"]:
                latency = stop["latency"]
                # current_stop = StopModel.objects()
                # place = PlaceModel.objects(id=stop_data["PlaceId"]).first()
                # day = DayModel.objects(id=stop["DayId"]).first()
                current_address = stop["Address"]
                if not day:
                    abort(404, description="Day not found")
                if stop_num > 0:
                    # prev_stop = StopModel.objects(id=stop["prev_stop"]).first()
                    prev_endtime = prev_stop.EndTime
                    prev_address = prev_stop.address

                    optimal_mode, duration, best_directions, best_distance_km = (
                        find_optimal_mode(prev_address, current_address, api_key)
                    )

                    # print(optimal_mode, duration)
                    long, lat = get_lat_long(current_address, api_key)
                    if optimal_mode:

                        starttime = prev_endtime + timedelta(minutes=int(duration / 60))
                        stp = StopModel(
                            Name=stop["Location"],
                            StartTime=starttime,
                            EndTime=starttime + timedelta(minutes=latency),
                            note=stop["Description"],
                            address=current_address,
                            transportation={},
                            # PlaceId=place.id,
                            DayId=day.id,
                            prev_stopId=str(prev_stop.id),
                            Isgreen=check_green(stop["Location"]),
                            coordinates=[long, lat],
                        )
                        stp.save()
                        prev_stop.transportation = {
                            "mode": optimal_mode,
                            "Timespent": int(duration / 60),
                            "distance": best_distance_km,
                            "LowCarbon": (
                                True
                                if optimal_mode not in ["driving", "TWO_WHEELER"]
                                else False
                            ),
                        }
                        prev_stop.save()
                        prev_stop = stp
                    #     transportation = TransportationModel(
                    # Name=optimal_mode,
                    # TimeSpent= int(duration/60),
                    # LowCarbon=True if optimal_mode != "driving" else False,
                    # FromStopId=prev_stop.id,
                    # ToStopId=stop.id,
                    #     )
                    #     transportation.save()

                    else:
                        abort(
                            500,
                            description=f"Fail to obtain the transportation between {prev_stop.Name} and {stop.Name}",
                        )

                else:
                    # parsed_date = datetime.strptime(str(day.Date), "%Y-%m-%d")
                    parsed_date = datetime.strptime(str(day.Date), "%Y-%m-%d %H:%M:%S")

                    new_date = parsed_date.replace(
                        hour=8, minute=0, second=0, microsecond=0
                    )
                    long, lat = get_lat_long(current_address, api_key)
                    # Convert back to string in yyyy-mm-dd hh:mm format
                    stp = StopModel(
                        Name=stop["Location"],
                        StartTime=new_date,
                        EndTime=new_date + timedelta(minutes=latency),
                        note=stop["Description"],
                        address=stop["Address"],
                        # PlaceId=place,
                        transportation={},
                        DayId=day,
                        Isgreen=check_green(stop["Location"]),
                        coordinates=[long, lat],
                    )
                    stp.save()
                    prev_stop = stp
                stop_num = stop_num + 1

            current_date += timedelta(days=1)
            daynum = daynum + 1

        data = jsonify({"message": f" Complete travelplan is created successfully"})
        return make_response(data, 201)





@blp.route("/CreateAll_demo_normal")
class TravelPlanList(MethodView):

    # @blp.arguments(CreateAllSchema)
    @jwt_required()
    def post(self):
        travel_plan_data = {
                    "startdate": "2024-11-20",
                    "enddate": "2024-11-20",
                    "planname": "台北一日遊",
                    "Plans": [
                        {
                            "Recommendation": [
                                {
                                    "Activity": "早餐",
                                    "Address": "台北市中正區忠孝東路一段108號2樓 ",
                                    "Description": "台北著名的早餐店，以傳統的豆漿和燒餅油條聞名。",
                                    "Location": "阜杭豆漿",
                                    "latency": 60
                                },
                                {
                                    "Activity": "景點參觀",
                                    "Address": "臺北市士林區雨聲街120號  ",
                                    "Description": "位於台北市的綠色生態園區，提供豐富的自然景觀和文化體驗。",
                                    "Location": "芝山文化生態綠園",
                                    "latency": 90
                                },
                                {
                                    "Activity": "午餐",
                                    "Address": "台北市信義區光復南路260巷39號",
                                    "Description": "氣氛輕鬆的餐廳採用復古時尚風裝潢，並供應各式種類的餐點。  ",
                                    "Location": "ABV Bar & Kitchen 地中海餐酒館 台北創始店",
                                    "latency": 90
                                },
                                {
                                    "Activity": "景點參觀",
                                    "Address": "台北市士林區至善路二段221號",
                                    "Description": "擁有豐富的中國古代藝術珍品，為世界著名的博物館之一",
                                    "Location": "國立故宮博物院",
                                    "latency": 180
                                },
                                {
                                    "Activity": "晚餐",
                                    "Address": "105台灣台北市松山區饒河街",
                                    "Description": "歷史悠久的熱鬧夜市，有各式商店和街頭小吃攤。",
                                    "Location": "饒河街觀光夜市",
                                    "latency": 120
                                }
                                
                            ]
                        },
                        
                    ]
                }

        # user_id = get_jwt_identity()
        travel_plan_data["startdate"] = datetime.strptime(travel_plan_data["startdate"], "%Y-%m-%d")
        travel_plan_data["enddate"] = datetime.strptime(travel_plan_data["enddate"], "%Y-%m-%d")
        print('ok')
        user_id = '672330196b182d387e7a240a'
        user = UserModel.objects(id=user_id).first()
        actual_days = (
            travel_plan_data["enddate"] - travel_plan_data["startdate"]
        ).days + 1
        if actual_days != len(travel_plan_data["Plans"]):
            abort(
                400,
                description="travel plan phase and the plans of day is inconsistent",
            )

        if not user:
            abort(404, description="User not found")
        api_key = os.getenv("GOOGLE_MAP_API_KEY")
        travel_plan = TravelPlanModel(
            planname=travel_plan_data["planname"],
            startdate=travel_plan_data["startdate"],
            enddate=travel_plan_data["enddate"],
            createAt=datetime.now(),
            userId=user.id,
        )
        travel_plan.save()
        daynum = 0
        current_date = travel_plan_data["startdate"]
        while current_date <= travel_plan_data["enddate"]:
            day = DayModel(
                Date=current_date,
                TravelPlanId=travel_plan.id,  # Associate the day with the travel plan
            )
            day.save()  # Save each DayModel instance to the database
            # days --> Plans
            stopListInDay = travel_plan_data["Plans"][daynum]
            stop_num = 0
            # stops --> Recommendation
            for stop in stopListInDay["Recommendation"]:
                latency = stop["latency"]
                # current_stop = StopModel.objects()
                # place = PlaceModel.objects(id=stop_data["PlaceId"]).first()
                # day = DayModel.objects(id=stop["DayId"]).first()
                current_address = stop["Address"]
                if not day:
                    abort(404, description="Day not found")
                if stop_num > 0:
                    # prev_stop = StopModel.objects(id=stop["prev_stop"]).first()
                    prev_endtime = prev_stop.EndTime
                    prev_address = prev_stop.address

                    optimal_mode, duration, best_directions, best_distance_km = (
                        find_optimal_mode(prev_address, current_address, api_key)
                    )

                    # print(optimal_mode, duration)
                    long, lat = get_lat_long(current_address, api_key)
                    if optimal_mode:

                        starttime = prev_endtime + timedelta(minutes=int(duration / 60))
                        stp = StopModel(
                            Name=stop["Location"],
                            StartTime=starttime,
                            EndTime=starttime + timedelta(minutes=latency),
                            note=stop["Description"],
                            address=current_address,
                            transportation={},
                            # PlaceId=place.id,
                            DayId=day.id,
                            prev_stopId=str(prev_stop.id),
                            Isgreen=check_green(stop["Location"]),
                            coordinates=[long, lat],
                        )
                        stp.save()
                        prev_stop.transportation = {
                            "mode": optimal_mode,
                            "Timespent": int(duration / 60),
                            "distance": best_distance_km,
                            "LowCarbon": (
                                True
                                if optimal_mode not in ["driving", "TWO_WHEELER"]
                                else False
                            ),
                        }
                        prev_stop.save()
                        prev_stop = stp
                    #     transportation = TransportationModel(
                    # Name=optimal_mode,
                    # TimeSpent= int(duration/60),
                    # LowCarbon=True if optimal_mode != "driving" else False,
                    # FromStopId=prev_stop.id,
                    # ToStopId=stop.id,
                    #     )
                    #     transportation.save()

                    else:
                        abort(
                            500,
                            description=f"Fail to obtain the transportation between {prev_stop.Name} and {stop.Name}",
                        )

                else:
                    # parsed_date = datetime.strptime(str(day.Date), "%Y-%m-%d")
                    parsed_date = datetime.strptime(str(day.Date), "%Y-%m-%d %H:%M:%S")

                    new_date = parsed_date.replace(
                        hour=8, minute=0, second=0, microsecond=0
                    )
                    long, lat = get_lat_long(current_address, api_key)
                    # Convert back to string in yyyy-mm-dd hh:mm format
                    stp = StopModel(
                        Name=stop["Location"],
                        StartTime=new_date,
                        EndTime=new_date + timedelta(minutes=latency),
                        note=stop["Description"],
                        address=stop["Address"],
                        # PlaceId=place,
                        transportation={},
                        DayId=day,
                        Isgreen=check_green(stop["Location"]),
                        coordinates=[long, lat],
                    )
                    stp.save()
                    prev_stop = stp
                stop_num = stop_num + 1

            current_date += timedelta(days=1)
            daynum = daynum + 1

        data = jsonify({"message": f" Complete travelplan is created successfully"})
        return make_response(data, 201)
