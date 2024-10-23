from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.user import UserModel
from models.travelPlan import TravelPlanModel
from models.day import DayModel
from models.stop import StopModel

from db import mongo
from Schema import UserSchema, AddTravelPlanSchema, UpdateTravelPlanSchema, CreateAllSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from datetime import datetime, timedelta
import os
from Route import (
    get_directions,
    get_duration_in_seconds,
    print_detailed_route_info,
    find_optimal_mode,
)
from datetime import datetime, timedelta

blp = Blueprint("TravelPlan", __name__, url_prefix="/travel_plans")


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
        daynum = 0
        current_date = travel_plan_data["startdate"]
        while current_date <= travel_plan_data["enddate"]:
            day = DayModel(
                Date=current_date,
                TravelPlanId=travel_plan.id,  # Associate the day with the travel plan
            )
            day.save()  # Save each DayModel instance to the database

            stopListInDay = travel_plan_data['days'][daynum]
            stop_num = 0
            for stop in stopListInDay['stops']:
                print(stop)
                latency = stop["latency"]
                # current_stop = StopModel.objects()
                # place = PlaceModel.objects(id=stop_data["PlaceId"]).first()
                # day = DayModel.objects(id=stop["DayId"]).first()
                current_address = stop["address"]
                if not day:
                    abort(404, description="Day not found")
                if stop_num > 0 :
                    # prev_stop = StopModel.objects(id=stop["prev_stop"]).first()
                    prev_endtime = prev_stop.EndTime
                    prev_address = prev_stop.address

                    api_key = os.getenv("GOOGLE_MAP_API_KEY")

                    optimal_mode, duration, best_directions = find_optimal_mode(
                        prev_address, current_address, api_key
                    )
                    print(optimal_mode, duration)

                    if optimal_mode:

                        starttime = prev_endtime + timedelta(minutes=int(duration / 60))
                        stp = StopModel(
                            Name=stop["stopname"],
                            StartTime=starttime,
                            EndTime=starttime + timedelta(minutes=latency),
                            note=stop["Note"],
                            address=current_address,
                            transportation={},
                            # PlaceId=place.id,
                            DayId=day.id,
                            prev_stopId=str(prev_stop.id),
                        )
                        stp.save()
                        prev_stop.transportation = {
                            "mode": optimal_mode,
                            "Timespent": int(duration / 60),
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
                    # parsed_date = datetime.strptime(day.Date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    # new_datetime = day.Date.replace(hour=8, minute=0, second=0, microsecond=0)
                    # latency = stop['latency']


                    # Extract the yyyy-mm-dd part and add 08:00 to it
                    # new_date = parsed_date.replace(hour=8, minute=0, second=0, microsecond=0)

                    # Convert back to string in yyyy-mm-dd hh:mm format
                    # formatted_date = new_date.strftime("%Y-%m-%d %H:%M"
                    stp = StopModel(
                        Name=stop["stopname"],
                        StartTime=stop["StartTime"],
                        EndTime=stop["StartTime"] + timedelta(minutes=latency),
                        note=stop["Note"],
                        address=stop['address'],
                        # PlaceId=place,
                        transportation={},
                        DayId=day,
                    )
                    stp.save()
                    prev_stop = stp
                stop_num = stop_num + 1


            current_date += timedelta(days=1)
            daynum = daynum + 1
        
        data = jsonify(
            {
                "message": f' Complete is created successfully'
            }
        )
        return make_response(data, 201)
