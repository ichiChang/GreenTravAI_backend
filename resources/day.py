# resources/day.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.day import DayModel
from models.travelPlan import TravelPlanModel
from Schema import DaySchema, AddDaySchema, UpdateDaySchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify

blp = Blueprint("Day", __name__, url_prefix="/days")


@blp.route("/")
class DayList(MethodView):

    @blp.arguments(AddDaySchema)
    @jwt_required()
    def post(self, day_data):
        travel_plan = TravelPlanModel.objects(id=day_data["TravelPlanId"]).first()
        if not travel_plan:
            abort(404, description="Travel plan not found")

        day = DayModel(
            Date=day_data["Date"],
            TravelPlanId=travel_plan,
        )
        day.save()
        return {"message": f'Day {day_data["Date"]} created successfully'}, 201

    @jwt_required()
    def get(self):
        days = DayModel.objects()
        return jsonify(days), 200


@blp.route("/<string:day_id>")
class DayItem(MethodView):

    @jwt_required()
    def get(self, day_id):
        day = DayModel.objects(id=day_id).first()
        if not day:
            abort(404, description="Day not found")
        return jsonify(day), 200

    @blp.arguments(UpdateDaySchema)
    @jwt_required()
    def put(self, update_data, day_id):
        DayModel.objects(id=day_id).update(**update_data)
        return {"message": "Day updated successfully"}

    @jwt_required()
    def delete(self, day_id):
        day = DayModel.objects(id=day_id).delete()
        if not day:
            abort(404, description="Day not found")
        return {"message": "Day deleted successfully"}
