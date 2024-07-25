from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.user import UserModel
from models.travelPlan import TravelPlanModel

from db import mongo
from Schema import UserSchema, AddTravelPlanSchema, UpdateTravelPlanSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from datetime import datetime

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
        data = jsonify({"message": f'{user.username} created a travel plan named {travel_plan_data["planname"]}'})
        return make_response(data,201)
        

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.objects(id=user_id).first()
        if not user:
            abort(404, description="User not found")

        travel_plans = TravelPlanModel.objects(userId=user.id)
        data =jsonify([
                {
                    "planname": plan.planname,
                    "startdate": plan.startdate,
                    "enddate": plan.enddate,
                    "createdAt": plan.createAt,
                }
                for plan in travel_plans
            ]) 
        return make_response(data,200)
        


@blp.route("/<string:plan_id>")
class TravelPlanItem(MethodView):

    @jwt_required()
    def get(self, plan_id):
        user_id = get_jwt_identity()
        travel_plan = TravelPlanModel.objects(id=plan_id,userId = user_id).first()
        if not travel_plan:
            abort(404, description="Travel plan not found")
        data = jsonify({
                "planname": travel_plan.planname,
                "startdate": travel_plan.startdate,
                "enddate": travel_plan.enddate,
                "createdAt": travel_plan.createAt,
            })
        return make_response(data,200)
        
        

    @blp.arguments(UpdateTravelPlanSchema)
    @jwt_required()
    def put(self, update_data, plan_id):
        user_id = get_jwt_identity()

        TravelPlanModel.objects(id=plan_id, userId=user_id).update(planname=update_data['Name'],startdate=update_data['StartDay'],enddate=update_data['EndDay'])
        data = jsonify({"message": "Travel plan updated successfully"})
        return make_response(data,200)
        

    @jwt_required()
    def delete(self, plan_id):
        user_id = get_jwt_identity()
        travel_plan = TravelPlanModel.objects(id=plan_id, userId=user_id).first()
        if not travel_plan:
            abort(404, description="Travel plan not found")
        travel_plan.delete()
        data = jsonify({"message": "Travel plan deleted successfully"})
        return make_response(data,200)
       