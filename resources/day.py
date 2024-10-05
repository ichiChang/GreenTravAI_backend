# resources/day.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.day import DayModel
from models.travelPlan import TravelPlanModel
from Schema import AddDaySchema, UpdateDaySchema, DayinPlanSchema, DaySchema
from flask_jwt_extended import jwt_required
from flask import jsonify, make_response
from datetime import timedelta


blp = Blueprint("Day", __name__, url_prefix="/days")


@blp.route("/")
class DayList(MethodView):

    @blp.arguments(DaySchema)
    @jwt_required()
    def post(self, day_data):
        # travel_plan = TravelPlanModel.objects(id=plan_id,).first()
        print("got here")

        travel_plan = TravelPlanModel.objects(
            id=day_data["TravelPlanId"],
        ).first()

        if not travel_plan:
            abort(404, description="Travel plan not found")

        day = DayModel(
            Date=day_data["Date"],
            TravelPlanId=travel_plan,
        )
        day.save()
        # return Response(
        #     response=jsonify({"message": f'Day {day_data["Date"]} created successfully'}),
        #     status=201,
        #     mimetype="application/json"

        # )
        data = jsonify({"message": f'Day {day_data["Date"]} created successfully'})
        return make_response(data, 201)
        # return {"message": f'Day {day_data["Date"]} created successfully'}, 201

    @jwt_required()
    def get(self):
        days = DayModel.objects()

        data = jsonify(days)
        return make_response(data, 200)


@blp.route("/<string:day_id>")
class DayItem(MethodView):

    @jwt_required()
    def get(self, day_id):
        day = DayModel.objects(id=day_id).first()
        if not day:
            abort(404, description="Day not found")

        data = jsonify(
            {
                "id": day.id,
                "date": day.Date.strftime("%Y-%m-%d"),
                "TravelPlanId": day.TravelPlanId.id,
            }
        )
        return make_response(data, 200)

    @blp.arguments(UpdateDaySchema)
    @jwt_required()
    def put(self, update_data, day_id):
        DayModel.objects(id=day_id).update(**update_data)

        data = jsonify({"message": "Day updated successfully"})
        return make_response(data, 200)

    @jwt_required()
    def delete(self, day_id):
        day = DayModel.objects(id=day_id).delete()
        if not day:
            abort(404, description="Day not found")

        data = jsonify({"message": "Day deleted successfully"})
        return make_response(data, 200)


@blp.route("/day-in-plan")
class DayinPlan(MethodView):

    @blp.arguments(DayinPlanSchema)
    @jwt_required()
    def post(self, plan_data):
        plan_id = plan_data["TravelPlanId"]

        days = DayModel.objects(TravelPlanId=plan_id)

        formatted_days = []
        for day in days:
            formatted_date_time = day.Date.strftime("%Y-%m-%d") if day.Date else None
            formatted_day = {
                "id": str(day.id),
                "date": formatted_date_time,
                "travel_plan_id": day.TravelPlanId.id,
            }
            formatted_days.append(formatted_day)

        data = jsonify(formatted_days)
        return make_response(data, 201)


@blp.route("/append-day-inTP")
class AppendDayinTP(MethodView):

    @blp.arguments(DayinPlanSchema)
    @jwt_required()
    def post(self, plan_data):
        plan_id = plan_data["TravelPlanId"]

        # Get the days for the specified TravelPlanId, sorted by Date in descending order
        latest_day = DayModel.objects(TravelPlanId=plan_id).order_by("-Date").first()

        if latest_day:
            # Get the latest Date and add one day
            new_date = latest_day.Date + timedelta(days=1)

            # Create a new Day object with the new date
            new_day = DayModel(
                TravelPlanId=plan_id,
                Date=new_date,
                # Add other necessary fields for the DayModel if required
            )
            new_day.save()

        data = jsonify(
            {
                "message": f"Day {new_day.Date} appended on travelplan {plan_id} successfully"
            }
        )
        return make_response(data, 201)
