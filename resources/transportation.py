from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.transportation import TransportationModel
from models.stop import StopModel
from Schema import (
    TransportationSchema,
    AddTransportationSchema,
    UpdateTransportationSchema,
    ChooseTransportationSchema,
    ChooseTransportationUpdateSchema,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response

from Route import (
    get_directions,
    get_duration_in_seconds,
    print_detailed_route_info,
    find_optimal_mode,
)
import os
from datetime import timedelta
from resources.TravelPlan import calcarbon


blp = Blueprint("Transportation", __name__, url_prefix="/transportations")


@blp.route("/")
class TransportationList(MethodView):

    @blp.arguments(AddTransportationSchema)
    @jwt_required()
    def post(self, transportation_data):
        from_stop = StopModel.objects(id=transportation_data["FromStopId"]).first()
        to_stop = StopModel.objects(id=transportation_data["ToStopId"]).first()
        if not from_stop or not to_stop:
            abort(404, description="FromStop or ToStop not found")

        transportation = TransportationModel(
            Name=transportation_data["Name"],
            TimeSpent=transportation_data["TimeSpent"],
            LowCarbon=transportation_data["LowCarbon"],
            FromStopId=from_stop,
            ToStopId=to_stop,
        )
        transportation.save()
        data = jsonify(
            {
                "message": f'Transportation {transportation_data["Name"]} created successfully'
            }
        )
        return make_response(data, 201)

    @jwt_required()
    def get(self):
        transportations = TransportationModel.objects()
        data = jsonify(transportations)
        return make_response(data, 200)


@blp.route("/<string:transportation_id>")
class TransportationItem(MethodView):

    @jwt_required()
    def get(self, transportation_id):
        transportation = TransportationModel.objects(id=transportation_id).first()
        if not transportation:
            abort(404, description="Transportation not found")

        data = jsonify(transportation)
        return make_response(data, 200)

    @blp.arguments(UpdateTransportationSchema)
    @jwt_required()
    def put(self, update_data, transportation_id):
        TransportationModel.objects(id=transportation_id).update(**update_data)

        data = jsonify({"message": "Transportation updated successfully"})
        return make_response(data, 200)

    @jwt_required()
    def delete(self, transportation_id):
        transportation = TransportationModel.objects(id=transportation_id).delete()
        if not transportation:
            abort(404, description="Transportation not found")
        data = jsonify({"message": "Transportation deleted successfully"})
        return make_response(data, 200)


@blp.route("/choose")
class TransportationChoose(MethodView):

    @blp.arguments(ChooseTransportationSchema)
    @jwt_required()
    def post(self, transportation_data):
        from_stop = StopModel.objects(id=transportation_data["FromStopId"]).first()
        to_stop = StopModel.objects(id=transportation_data["ToStopId"]).first()
        if not from_stop or not to_stop:
            abort(404, description="FromStop or ToStop not found")
        api_key = os.getenv("GOOGLE_MAP_API_KEY")

        modes = ["driving", "walking", "bicycling", "transit", "TWO_WHEELER"]
        res = {}
        car_directions = get_directions(
            from_stop.address, to_stop.address, "driving", api_key
        )
        car_duration, car_best_distance_km = get_duration_in_seconds(car_directions)
        car_emission = calcarbon(car_best_distance_km, "driving")
        for mode in modes:
            if mode == "driving":
                emission = car_emission
                duration = car_duration
            else:
                directions = get_directions(
                    from_stop.address, to_stop.address, mode, api_key
                )
                duration, best_distance_km = get_duration_in_seconds(directions)

                emission = calcarbon(best_distance_km, mode)
            if car_emission > 0:
                # emission_rate = int((1 - round((emission/car_emission),2)) * 100)
                emission_rate = int(car_emission - emission)
            else:
                emission_rate = 0
            res[mode] = {
                "Timespent": int(duration / 60),
                "emission_reduction_amount": emission_rate,
            }

        data = jsonify(res)
        return make_response(data, 201)

    @blp.arguments(ChooseTransportationUpdateSchema)
    @jwt_required()
    def put(self, transportation_data):
        from_stop = StopModel.objects(id=transportation_data["FromStopId"]).first()
        mode = transportation_data["mode"]
        TimeSpent = transportation_data["TimeSpent"]
        if not from_stop:
            abort(404, description="FromStop not found")
        new_trans = {
            "mode": mode,
            "Timespent": TimeSpent,
            "LowCarbon": True if mode not in ["driving", "TWO_WHEELER"] else False,
        }
        from_stop.transportation = new_trans
        from_stop.save()

        curr_stop = from_stop
        next_stop = StopModel.objects(
            prev_stopId=transportation_data["FromStopId"]
        ).first()
        while next_stop:
            curr_endtime = curr_stop.EndTime
            curr_timespent = curr_stop.transportation.get("Timespent")
            next_new_latency = int(
                (next_stop.EndTime - next_stop.StartTime).total_seconds() / 60
            )
            next_stop.StartTime = curr_endtime + timedelta(minutes=curr_timespent)
            next_stop.EndTime = (
                curr_endtime + timedelta(minutes=curr_timespent)
            ) + timedelta(minutes=next_new_latency)

            curr_stop.save()
            next_stop.save()

            temp_id = next_stop.id
            curr_stop = next_stop
            next_stop = StopModel.objects(prev_stopId=str(temp_id)).first()

        data = jsonify({"message": "Transportation updated successfully"})
        return make_response(data, 200)
