# resources/stop.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.stop import StopModel
from models.place import PlaceModel
from models.day import DayModel
from models.travelPlan import TravelPlanModel
from Schema import (
    StopSchema,
    AddStopSchema,
    UpdateStopSchema,
    LinkStopSchema,
    StopinDaySchema,
    EditStopSchema,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from Route import (
    get_directions,
    get_duration_in_seconds,
    print_detailed_route_info,
    find_optimal_mode,
)

# from models.transportation import TransportationModel
from bson import ObjectId
import os
from datetime import timedelta

blp = Blueprint("Stop", __name__, url_prefix="/stops")


@blp.route("/")
class StopList(MethodView):

    @blp.arguments(AddStopSchema)
    @jwt_required()
    def post(self, stop_data):

        latency = stop_data["latency"]
        current_stop = StopModel.objects()
        # place = PlaceModel.objects(id=stop_data["PlaceId"]).first()
        day = DayModel.objects(id=stop_data["DayId"]).first()
        current_address = stop_data["address"]
        if not day:
            abort(404, description="Day not found")
        if stop_data["prev_stop"] is not None:
            prev_stop = StopModel.objects(id=stop_data["prev_stop"]).first()
            prev_endtime = prev_stop.EndTime
            prev_address = prev_stop.address

            api_key = os.getenv("GOOGLE_MAP_API_KEY")

            optimal_mode, duration, best_directions = find_optimal_mode(
                prev_address, current_address, api_key
            )
            print(optimal_mode, duration)

            if optimal_mode:

                starttime = prev_endtime + timedelta(minutes=int(duration / 60))
                stop = StopModel(
                    Name=stop_data["Name"],
                    StartTime=starttime,
                    EndTime=starttime + timedelta(minutes=latency),
                    note=stop_data["note"],
                    address=current_address,
                    transportation={},
                    # PlaceId=place.id,
                    DayId=day.id,
                )
                stop.save()
                prev_stop.transportation = {
                    "mode": optimal_mode,
                    "Timespent": int(duration / 60),
                    "LowCarbon": True if optimal_mode != "driving" else False,
                }
                prev_stop.save()
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

            stop = StopModel(
                Name=stop_data["Name"],
                StartTime=stop_data["StartTime"],
                EndTime=stop_data["StartTime"] + timedelta(minutes=latency),
                note=stop_data["note"],
                address=current_address,
                # PlaceId=place,
                transportation={},
                DayId=day,
            )
            stop.save()
        data = jsonify({"message": f'Stop {stop_data["Name"]} created successfully'})
        return make_response(data, 201)

    @jwt_required()
    def get(self):
        stops = StopModel.objects()

        data = jsonify(stops)
        return make_response(data, 200)


@blp.route("/<string:stop_id>")
class StopItem(MethodView):

    @jwt_required()
    def get(self, stop_id):
        stop = StopModel.objects(id=stop_id).first()
        if not stop:
            abort(404, description="Stop not found")

        data = jsonify(
            {
                "id": stop.id,
                "Name": stop.Name,
                "StartTime": stop.StartTime.strftime("%Y-%m-%d %H:%M"),
                "EndTime": stop.EndTime.strftime("%Y-%m-%d %H:%M"),
                "note": stop.note,
                "address": stop.address,
                "DayId": stop.DayId.id,
            }
        )

        return make_response(data, 200)

    @blp.arguments(UpdateStopSchema)
    @jwt_required()
    def put(self, update_data, stop_id):
        StopModel.objects(id=stop_id).update(**update_data)

        data = jsonify({"message": "Stop updated successfully"})
        return make_response(data, 200)

    @jwt_required()
    def delete(self, stop_id):
        stop = StopModel.objects(id=stop_id).delete()
        if not stop:
            abort(404, description="Stop not found")
        data = jsonify({"message": "Stop deleted successfully"})
        return make_response(data, 200)


# @blp.route("/link")
# class StopLink(MethodView):

#     @blp.arguments(LinkStopSchema)
#     @jwt_required()
#     def post(self, stop_data):
#         origin_stop = StopModel.objects(id=stop_data["origin_Sid"]).first()
#         dest_stop = StopModel.objects(id=stop_data["dest_Sid"]).first()
#         # origin_pid = origin_stop.PlaceId
#         # dest_pid = dest_stop.PlaceId
#         origin_address = origin_stop.PlaceId.address
#         dest_address = dest_stop.PlaceId.address

#         # origin_address = PlaceModel.objects(id=ObjectId(origin_stop.PlaceId)).first().address
#         # dest_address = PlaceModel.objects(id=ObjectId(dest_stop.PlaceId)).first().address


#         api_key = os.getenv("GOOGLE_MAP_API_KEY")

#         optimal_mode, duration, best_directions = find_optimal_mode(origin_address, dest_address, api_key)


#         if optimal_mode:

#             transportation = TransportationModel(
#             Name=optimal_mode,
#             TimeSpent= int(duration/60),
#             LowCarbon=True if optimal_mode != "driving" else False,
#             FromStopId=stop_data["origin_Sid"],
#             ToStopId=stop_data["dest_Sid"],
#         )
#             transportation.save()
#             data = jsonify({"message": f'Link  origin {origin_stop.Name} and dest{dest_stop.Name} with {optimal_mode} ',
#                             "trans_mode": optimal_mode,
#                             "TimeSpend":int(duration/60),
#                             "LowCarbon":transportation.LowCarbon}
#                             )

#             return make_response(data,201)

#         abort(
#                 500,
#                 description=f"Fail to obtain the transportation between {origin_stop.Name} and {dest_stop.Name}",
#             )


@blp.route("/StopinDay")
class StopinDay(MethodView):

    @blp.arguments(StopinDaySchema)
    @jwt_required()
    def post(self, stop_data):

        stops = StopModel.objects(
            DayId=stop_data["day_id"],
        ).order_by("StartTime")

        stops_data = [
            {
                "id": stop.id,
                "stopname": stop.Name,
                "StartTime": stop.StartTime.strftime("%Y-%m-%d %H:%M"),
                "EndTime": stop.EndTime.strftime("%Y-%m-%d %H:%M"),
                "Note": stop.note,
                "Address": stop.address,
                "transportationToNext": {
                    "Mode": stop.transportation.get("mode"),
                    "TimeSpent": stop.transportation.get("Timespent"),
                    "LowCarbon": stop.transportation.get("LowCarbon"),
                },
            }
            for stop in stops
        ]

        data = jsonify({"day_id": stop_data["day_id"], "stops": stops_data})

        return make_response(data, 201)


@blp.route("/EditStop")
class EditStop(MethodView):

    @blp.arguments(EditStopSchema)
    @jwt_required()
    def post(self, stop_data):
        stops = stop_data["stops"]
        res_data = []
        count = 0
        for stop in stops:
            current_stop = StopModel.objects(id=stop["stop_id"]).first()
            prev_stop = StopModel.objects(id=stop["previous_stop_id"]).first() or None

            if prev_stop is None:
                latency = int(
                    (current_stop.EndTime - current_stop.StartTime).total_seconds() / 60
                )
                current_day = current_stop.DayId
                root_starttime = (
                    StopModel.objects(DayId=current_day)
                    .order_by("StartTime")
                    .first()
                    .StartTime
                )
                current_stop.StartTime = root_starttime
                current_stop.EndTime = root_starttime + timedelta(minutes=latency)
                current_stop.transportation = {}

                current_stop.save()

            else:
                current_addr = current_stop.address
                prev_addr = prev_stop.address
                api_key = os.getenv("GOOGLE_MAP_API_KEY")

                optimal_mode, duration, best_directions = find_optimal_mode(
                    prev_addr, current_addr, api_key
                )

                # current_stop.StartTime = prev_stop.EndTime
                if optimal_mode:

                    prev_endtime = prev_stop.EndTime
                    starttime = prev_endtime + timedelta(minutes=int(duration / 60))

                    current_stop.StartTime = starttime
                    current_stop.EndTime = starttime + timedelta(minutes=latency)
                    current_stop.transportation = {}

                    current_stop.save()

                    prev_stop.transportation = {
                        "mode": optimal_mode,
                        "Timespent": int(duration / 60),
                        "LowCarbon": True if optimal_mode != "driving" else False,
                    }
                    prev_stop.save()
            if count == len(stops) - 1:
                res_data.append(prev_stop)
                res_data.append(current_stop)

            else:
                if prev_stop is not None:
                    res_data.append(prev_stop)
            count += 1

        data = jsonify({"stops": res_data})

        return make_response(data, 201)
