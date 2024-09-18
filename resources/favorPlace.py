from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.favorPlace import favorPlaceModel
from models.stop import StopModel
from Schema import FavorPlaceSchema, RetrieveFavorPlaceSchema

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response

blp = Blueprint("Favorplace", __name__, url_prefix="/favorplace")

@blp.route("/")
class FavorPLaceList(MethodView):

    @blp.arguments(FavorPlaceSchema)
    @jwt_required()
    def post(self, favorplace_data):
        if favorPlaceModel.objects.filter(UserId=favorplace_data["UserId"], PlaceId=favorplace_data["PlaceId"]).first() :
            abort(404, description="favorplace is already exist")

        favorplace = favorPlaceModel(
            UserId=favorplace_data["UserId"],
            PlaceId=favorplace_data["PlaceId"],
            
        )
        favorplace.save()
        data = jsonify({"message": f'favorplace {favorplace} created successfully'})
        return make_response(data,201)
        

    @jwt_required()
    def get(self):
        favorplace = favorplace.objects()
        data = jsonify(favorplace)
        return make_response(data,200)

@blp.route("/retrieve-favor")
class RetrieveFavorPLace(MethodView):

    @blp.arguments(RetrieveFavorPlaceSchema)
    @jwt_required()
    def post(self, favorplace_data):
        favorplaces = favorPlaceModel.objects.filter(UserId=favorplace_data["UserId"])

        data = jsonify(favorplaces)
        return make_response(data,201)



@blp.route("/<string:favorplace_id>")
class favorplaceItem(MethodView):

    @jwt_required()
    def delete(self, favorplace_id):
        favorplace = favorPlaceModel.objects(id=favorplace_id).delete()
        if not favorplace:
            abort(404, description="favorplace not found")
        data = jsonify({"message": "favorplace deleted successfully"})
        return make_response(data,200)
