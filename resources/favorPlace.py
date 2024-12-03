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

    # @blp.arguments(FavorPlaceSchema)
    # @jwt_required()
    # def post(self):
    #     current_user = get_jwt_identity()
    #     print(current_user)
    #     existing_favorplace = favorPlaceModel.objects.filter(
    #         UserId=current_user, PlaceId=favorplace_data["PlaceId"]
    #     ).first()

    #     if existing_favorplace:
    #         if not existing_favorplace.is_deleted:
    #             abort(404, description="favorplace already exists and is active")
    #         else:
    #             # Reactivate the favorplace if it was marked as deleted
    #             existing_favorplace.is_deleted = False
    #             existing_favorplace.save()
    #             data = jsonify(
    #                 {
    #                     "message": f"favorplace {existing_favorplace} reactivated successfully"
    #                 }
    #             )
    #             return make_response(data, 200)

    #     # Create a new favorplace if it doesn't exist
    #     favorplace = favorPlaceModel(
    #         UserId=favorplace_data["UserId"],
    #         PlaceId=favorplace_data["PlaceId"],
    #     )
    #     favorplace.save()
    #     data = jsonify({"message": f"favorplace {favorplace} created successfully"})
    #     return make_response(data, 201)

    @jwt_required()
    def get(self):
        favorplace = favorplace.objects()
        data = jsonify(favorplace)
        return make_response(data, 200)


@blp.route("/items/")
class RetrieveFavorPLace(MethodView):

    # @blp.arguments(RetrieveFavorPlaceSchema)
    @jwt_required()
    def get(self):
        # Filter by UserId and ensure only active favorplaces are retrieved
        current_user = get_jwt_identity()
        favorplaces = favorPlaceModel.objects.filter(
            UserId=current_user, is_deleted=False
        )

        # Extract the list of PlaceIds
        place_ids = [favorplace.PlaceId for favorplace in favorplaces]

        # Return the list of place_ids with the key "places"
        data = jsonify({"places": place_ids})
        return make_response(data, 200)


@blp.route("/<string:favorplace_id>")
class favorplaceItem(MethodView):

    @jwt_required()
    def post(self, favorplace_id):
        current_user = get_jwt_identity()
        # print(current_user)
        existing_favorplace = favorPlaceModel.objects.filter(
            UserId=current_user, PlaceId=favorplace_id
        ).first()

        if existing_favorplace:
            if not existing_favorplace.is_deleted:
                abort(404, description="favorplace already exists and is active")
            else:
                # Reactivate the favorplace if it was marked as deleted
                existing_favorplace.is_deleted = False
                existing_favorplace.save()
                data = jsonify(
                    {
                        "message": f"favorplace {existing_favorplace} reactivated successfully"
                    }
                )
                return make_response(data, 200)

        # Create a new favorplace if it doesn't exist
        favorplace = favorPlaceModel(
            UserId=current_user, PlaceId=favorplace_id, is_deleted=False
        )
        favorplace.save()
        data = jsonify({"message": f"favorplace {favorplace} created successfully"})
        return make_response(data, 201)

    @jwt_required()
    def put(self, favorplace_id):
        favorplace = favorPlaceModel.objects(id=favorplace_id).first()

        if not favorplace:
            abort(404, description="favorplace not found")

        current_user = get_jwt_identity()
        
        if str(favorplace.UserId.id) != current_user:
            abort(403, description="Unauthorized to delete this favorplace")

        favorplace.is_deleted = True
        favorplace.save()

        data = jsonify({"message": "favorplace has deleted successfully"})
        return make_response(data, 201)
