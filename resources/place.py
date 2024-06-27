# resources/place.py
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from models.place import PlaceModel
from Schema import PlaceSchema
from services.google_storage import upload_image_to_gcs
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required

blp = Blueprint("places", __name__, url_prefix="/places")


@blp.route("/")
class Places(MethodView):

    @jwt_required()
    def get(self):
        # Retrieve all places
        places = PlaceModel.objects()
        return jsonify(places), 200

    @blp.arguments(PlaceSchema, location="form")
    @blp.response(200, PlaceSchema)
    def post(self, args):
        image = request.files.get("Image")
        new_data = request.form.to_dict()  # 从 form-data 中获取其他数据
        if image:
            filename = secure_filename(image.filename)
            image_url = upload_image_to_gcs(image.read(), filename, image.content_type)
            new_data["image"] = image_url
        place = Place.create(**new_data)
        return place


@blp.route("/<string:id>")
class Place(MethodView):

    @blp.arguments(PlaceSchema)
    @jwt_required()
    def put(self, update_data, id):
        # Update a place with validated data
        image = request.files.get("image")
        place = PlaceModel.objects(id=id).first()
        if place:
            if image:
                filename = secure_filename(image.filename)
                image_url = upload_image_to_gcs(
                    image.read(), filename, image.content_type
                )
                update_data["Image"] = image_url
            place.update(**update_data)
            return jsonify(place), 200
        else:
            return jsonify(error="Place not found"), 404

    @jwt_required()
    def get(self, id):
        # Retrieve a single place by id
        place = PlaceModel.objects(id=id).first()
        if place:
            return jsonify(place), 200
        else:
            return jsonify(error="Place not found"), 404

    @jwt_required()
    def delete(self, id):
        # Delete a place
        place = PlaceModel.objects(id=id).delete()
        if place:
            return jsonify(success=True), 200
        else:
            return jsonify(error="Place not found"), 404
