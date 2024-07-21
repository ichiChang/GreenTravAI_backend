from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.transportation import TransportationModel
from models.stop import StopModel
from Schema import (
    TransportationSchema,
    AddTransportationSchema,
    UpdateTransportationSchema,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, Response

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
        return Response(
            response=jsonify({"message": f'Transportation {transportation_data["Name"]} created successfully'}),
            status=201,
            mimetype="application/json"
        )

    @jwt_required()
    def get(self):
        transportations = TransportationModel.objects()
        return Response(
            response=jsonify(transportations),
            status=200,
            mimetype="application/json"
        )


@blp.route("/<string:transportation_id>")
class TransportationItem(MethodView):

    @jwt_required()
    def get(self, transportation_id):
        transportation = TransportationModel.objects(id=transportation_id).first()
        if not transportation:
            abort(404, description="Transportation not found")
        return Response(
            response=jsonify(transportation),
            status=200,
            mimetype="application/json"
        )


    @blp.arguments(UpdateTransportationSchema)
    @jwt_required()
    def put(self, update_data, transportation_id):
        TransportationModel.objects(id=transportation_id).update(**update_data)
        return Response(
            response=jsonify({"message": "Transportation updated successfully"}),
            status=200,
            mimetype="application/json"
        )

    @jwt_required()
    def delete(self, transportation_id):
        transportation = TransportationModel.objects(id=transportation_id).delete()
        if not transportation:
            abort(404, description="Transportation not found")
        return Response(
            response=jsonify({"message": "Transportation deleted successfully"}),
            status=200,
            mimetype="application/json"
        )
