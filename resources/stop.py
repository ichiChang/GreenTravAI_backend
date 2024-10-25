# resources/stop.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.stop import StopModel
from models.place import PlaceModel
from models.day import DayModel
from models.green_dict import GreenDictModel
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


def check_green(stop_name):

    return GreenDictModel.objects(spot_name=stop_name).first() is not None



def format_stop(stop):
    return {
        "id": stop.id,
        "stopname": stop.Name,
        "StartTime": stop.StartTime.strftime("%Y-%m-%d %H:%M"),
        "EndTime": stop.EndTime.strftime("%Y-%m-%d %H:%M"),
        "Note": stop.note,
        "Address": stop.address,
        "prev_stop": stop.prev_stopId,
        "Isgreen":stop.Isgreen,
        "transportationToNext": {
            "Mode": stop.transportation.get("mode"),
            "TimeSpent": stop.transportation.get("Timespent"),
            "LowCarbon": stop.transportation.get("LowCarbon"),
        },
    }


@blp.route("/")
class StopList(MethodView):

    @blp.arguments(AddStopSchema)
    @jwt_required()
    def post(self, stop_data):

        latency = stop_data["latency"]
        # current_stop = StopModel.objects()
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

            optimal_mode, duration, best_directions, best_distance_km = (
                find_optimal_mode(prev_address, current_address, api_key)
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
                    prev_stopId=stop_data["prev_stop"],
                    Isgreen=check_green(stop_data["Name"])
                )
                stop.save()
                prev_stop.transportation = {
                    "mode": optimal_mode,
                    "Timespent": int(duration / 60),
                    "distance": int(best_distance_km),
                    "LowCarbon": (
                        True
                        if optimal_mode not in ["driving", "TWO_WHEELER"]
                        else False
                    ),
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
                Isgreen=check_green(stop_data["Name"])
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

        data = jsonify(format_stop(stop))

        return make_response(data, 200)

    @jwt_required()
    def delete(self, stop_id):
        stop = StopModel.objects(id=stop_id).first()
        if not stop:
            abort(404, description="Stop not found")

        transportation = stop.transportation

        if not (
            transportation.get("mode") is None
            and transportation.get("Timespent") is None
            and transportation.get("LowCarbon") is None
        ):
            abort(500, description="Stop is not in tail, cannot be deleted")

        prev_stop = StopModel.objects(id=stop.prev_stopId).first()
        if prev_stop:
            prev_stop.transportation = {}
            prev_stop.save()

        stop.delete()
        data = jsonify({"message": "Stop is deleted successfully"})
        return make_response(data, 200)

    @blp.arguments(UpdateStopSchema)
    @jwt_required()
    def put(self, update_data, stop_id):
        is_effectNext = False
        stop = StopModel.objects(id=stop_id).first()
        if update_data.get("note") is not None:
            stop.note = update_data.get("note")
            # stop.save()
        if (
            update_data.get("Name") is not None
            and update_data.get("address") is not None
        ):
            is_effectNext = True
            stop.Name = update_data.get("Name")
            stop.address = update_data.get("address")
            stop.Isgreen=check_green(update_data.get("Name"))
            prev_stop = StopModel.objects(id=stop.prev_stopId).first()
            if prev_stop:
                api_key = os.getenv("GOOGLE_MAP_API_KEY")

                optimal_mode, duration, best_directions, best_distance_km = (
                    find_optimal_mode(
                        prev_stop.address, update_data.get("address"), api_key
                    )
                )
                prev_stop.transportation = {
                    "mode": optimal_mode,
                    "Timespent": int(duration / 60),
                    "distance": int(best_distance_km),
                    "LowCarbon": (
                        True
                        if optimal_mode not in ["driving", "TWO_WHEELER"]
                        else False
                    ),
                }
                prev_stop.save()

                curr_latency = int((stop.EndTime - stop.StartTime).total_seconds() / 60)
                stop.StartTime = prev_stop.EndTime + timedelta(
                    minutes=int(duration / 60)
                )
                stop.EndTime = (
                    prev_stop.EndTime + timedelta(minutes=int(duration / 60))
                ) + timedelta(minutes=curr_latency)
                # stop.save()
            next_stop = StopModel.objects(prev_stopId=str(stop.id)).first()
            if next_stop:
                api_key = os.getenv("GOOGLE_MAP_API_KEY")

                optimal_mode, duration, best_directions, best_distance_km = (
                    find_optimal_mode(
                        update_data.get("address"), next_stop.address, api_key
                    )
                )
                stop.transportation = {
                    "mode": optimal_mode,
                    "Timespent": int(duration / 60),
                    "distance": int(best_distance_km),
                    "LowCarbon": (
                        True
                        if optimal_mode not in ["driving", "TWO_WHEELER"]
                        else False
                    ),
                }
        stop.save()

        if update_data.get("latency") is not None:
            is_effectNext = True
            stop.EndTime = stop.StartTime + timedelta(
                minutes=update_data.get("latency")
            )
            stop.save()

        if is_effectNext:
            next_stop = StopModel.objects(prev_stopId=str(stop.id)).first()
            curr_stop = stop

            while next_stop:
                next_latency = int(
                    (next_stop.EndTime - next_stop.StartTime).total_seconds() / 60
                )
                print(next_latency)
                timespent = curr_stop.transportation.get("Timespent")
                next_stop.StartTime = curr_stop.EndTime + timedelta(minutes=(timespent))
                next_stop.EndTime = (
                    curr_stop.EndTime + timedelta(minutes=(timespent))
                ) + timedelta(minutes=next_latency)
                print(next_stop.EndTime)
                next_stop.save()
                temp_id = next_stop.id
                curr_stop = next_stop
                next_stop = StopModel.objects(prev_stopId=str(temp_id)).first()
                print("ok")

        data = jsonify({"message": "Stop updated successfully"})
        return make_response(data, 200)

    # @jwt_required()
    # def delete(self, stop_id):
    #     stop = StopModel.objects(id=stop_id).delete()
    #     if not stop:
    #         abort(404, description="Stop not found")
    #     data = jsonify({"message": "Stop deleted successfully"})
    #     return make_response(data, 200)


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
                "prev_stop": stop.prev_stopId,
                "Isgreen":stop.Isgreen,
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
        day_id = StopModel.objects(id=stops[0]["stop_id"]).first().DayId.id
        res_data = []
        count = 0
        for stop in stops:
            current_stop = StopModel.objects(id=stop["stop_id"]).first()
            prev_stop = StopModel.objects(id=stop["previous_stop_id"]).first() or None
            latency = int(
                (current_stop.EndTime - current_stop.StartTime).total_seconds() / 60
            )

            if prev_stop is None:
                # latency = int(
                #     (current_stop.EndTime - current_stop.StartTime).total_seconds() / 60
                # )
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
                current_stop.prev_stopId = None

                current_stop.save()

            else:
                current_addr = current_stop.address
                prev_addr = prev_stop.address
                api_key = os.getenv("GOOGLE_MAP_API_KEY")

                optimal_mode, duration, best_directions, best_distance_km = (
                    find_optimal_mode(prev_addr, current_addr, api_key)
                )

                # current_stop.StartTime = prev_stop.EndTime
                if optimal_mode:

                    prev_endtime = prev_stop.EndTime
                    starttime = prev_endtime + timedelta(minutes=int(duration / 60))

                    current_stop.StartTime = starttime
                    current_stop.EndTime = starttime + timedelta(minutes=latency)
                    current_stop.transportation = {}
                    current_stop.prev_stopId = stop["previous_stop_id"]

                    current_stop.save()

                    prev_stop.transportation = {
                        "mode": optimal_mode,
                        "Timespent": int(duration / 60),
                        "distance": int(best_distance_km),
                        "LowCarbon": (
                            True
                            if optimal_mode not in ["driving", "TWO_WHEELER"]
                            else False
                        ),
                    }
                    prev_stop.save()
            if count == len(stops) - 1:
                res_data.append(format_stop(prev_stop))
                res_data.append(format_stop(current_stop))

            else:
                if prev_stop is not None:
                    res_data.append(format_stop(prev_stop))
            count += 1

        data = jsonify({"day_id": day_id, "stops": res_data})

        return make_response(data, 201)
