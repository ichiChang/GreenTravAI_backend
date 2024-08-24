# resources/stop.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.stop import StopModel
from models.place import PlaceModel
from models.day import DayModel
from models.travelPlan import TravelPlanModel
from Schema import StopSchema, AddStopSchema, UpdateStopSchema, LinkStopSchema, StopinDaySchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from Route import get_directions, get_duration_in_seconds, print_detailed_route_info, find_optimal_mode
from models.transportation import TransportationModel
from bson import ObjectId
import os

blp = Blueprint("Stop", __name__, url_prefix="/stops")


@blp.route("/")
class StopList(MethodView):

    @blp.arguments(AddStopSchema)
    @jwt_required()
    def post(self, stop_data):
        place = PlaceModel.objects(id=stop_data["PlaceId"]).first()
        day = DayModel.objects(id=stop_data["DayId"]).first()
        if not place or not day:
            abort(404, description="Place or Day not found")

        stop = StopModel(
            Name=stop_data["Name"],
            StartTime=stop_data["StartTime"],
            EndTime=stop_data["EndTime"],
            note=stop_data["note"],
            PlaceId=place,
            DayId=day,
        )
        stop.save()
        data = jsonify({"message": f'Stop {stop_data["Name"]} created successfully'})
        return make_response(data,201)
        

    @jwt_required()
    def get(self):
        stops = StopModel.objects()

        data = jsonify(stops)
        return make_response(data,200)
    
        


@blp.route("/<string:stop_id>")
class StopItem(MethodView):

    @jwt_required()
    def get(self, stop_id):
        stop = StopModel.objects(id=stop_id).first()
        if not stop:
            abort(404, description="Stop not found")

        data = jsonify(stop)
        return make_response(data,200)
        

    @blp.arguments(UpdateStopSchema)
    @jwt_required()
    def put(self, update_data, stop_id):
        StopModel.objects(id=stop_id).update(**update_data)

        data = jsonify({"message": "Stop updated successfully"})
        return make_response(data,200)
        


    @jwt_required()
    def delete(self, stop_id):
        stop = StopModel.objects(id=stop_id).delete()
        if not stop:
            abort(404, description="Stop not found")
        data = jsonify({"message": "Stop deleted successfully"})
        return make_response(data,200)

@blp.route("/link")
class StopLink(MethodView):

    @blp.arguments(LinkStopSchema)
    @jwt_required()
    def post(self, stop_data):
        origin_stop = StopModel.objects(id=stop_data["origin_Sid"]).first()
        dest_stop = StopModel.objects(id=stop_data["dest_Sid"]).first()
        # origin_pid = origin_stop.PlaceId
        # dest_pid = dest_stop.PlaceId
        origin_address = origin_stop.PlaceId.address
        dest_address = dest_stop.PlaceId.address

        # origin_address = PlaceModel.objects(id=ObjectId(origin_stop.PlaceId)).first().address
        # dest_address = PlaceModel.objects(id=ObjectId(dest_stop.PlaceId)).first().address


            
        api_key = os.getenv("GOOGLE_MAP_API_KEY")

        optimal_mode, duration, best_directions = find_optimal_mode(origin_address, dest_address, api_key)
        

        if optimal_mode:
       
            transportation = TransportationModel(
            Name=optimal_mode,
            TimeSpent= int(duration/60),
            LowCarbon=True if optimal_mode != "driving" else False,
            FromStopId=stop_data["origin_Sid"],
            ToStopId=stop_data["dest_Sid"],
        )
            transportation.save()
            data = jsonify({"message": f'Link  origin {origin_stop.Name} and dest{dest_stop.Name} with {optimal_mode} ',
                            "trans_mode": optimal_mode,
                            "TimeSpend":int(duration/60),
                            "LowCarbon":transportation.LowCarbon}
                            )
            
            return make_response(data,201)
        
        abort(
                500,
                description=f"Fail to obtain the transportation between {origin_stop.Name} and {dest_stop.Name}",
            )








@blp.route("/StopinDay")
class StopinDay(MethodView):

    @blp.arguments(StopinDaySchema)
    @jwt_required()
    def post(self, stop_data):
            
            stops = StopModel.objects(DayId=stop_data["day_id"],).order_by("StartTime")
            


            stops_data = [
        {
            "planname": stop.Name,
            "StartTime": stop.StartTime,
            "EndTime": stop.EndTime,
            "Note": stop.note,
            "transportationToNext": {
                "Mode": transportation.Name,
                "TimeSpent": transportation.TimeSpent,
                "LowCarbon": transportation.LowCarbon
            } if (transportation := TransportationModel.objects(FromStopId=stop.id).first()) else {}
        }
        for stop in stops
    ]
            

            data = jsonify({"day_id":stop_data["day_id"],
                            "stops":stops_data})

            return make_response(data,201)


            

            











       
            

        
        


        
        
