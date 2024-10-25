# resources/place.py
from flask import request, jsonify, make_response
from flask.views import MethodView
from flask_smorest import Blueprint
from models.place import PlaceModel
from models.green_dict import GreenDictModel
from Schema import PlaceSchema, InsertGreenSchema
from services.google_storage import upload_image_to_gcs
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
import traceback

blp = Blueprint("places", __name__, url_prefix="/places")


@blp.route("/")
class Places(MethodView):

    def get(self):
        # Retrieve all places
        places = PlaceModel.objects()

        data = jsonify(places)
        return make_response(data, 200)

    @blp.arguments(PlaceSchema, location="files")
    @jwt_required()
    def post(self, place_data):
        try:
            # 检查 image 字段是否存在于 request.files 中
            image = request.files.get("image")
            if image:
                filename = secure_filename(image.filename)
                image_url = upload_image_to_gcs(
                    image.read(), filename, image.content_type
                )
            else:
                image_url = None  # 没有图片时的处理

            # 从 request.form 中获取其他字段

            place = PlaceModel(
                placename=request.form.get("placename"),
                openingTime=request.form.get("openingTime"),
                address=request.form.get("address"),
                long=request.form.get("long"),
                lat=request.form.get("lat"),
                rating=float(request.form.get("rating")),
                lowCarbon=request.form.get("lowCarbon") == "true",
                image=image_url,
            )
            place.save()

            data = jsonify(
                {
                    "message": f'Place named {request.form.get("placename")} created successfully'
                }
            )
            return make_response(data, 201)

        except Exception as e:
            # 打印异常到控制台
            traceback.print_exc()
            data = jsonify({"error": str(e)})
            return make_response(data, 400)
            # 返回错误信息给客户端


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

            # place.reload()

            response_data = {
                "message": "Place successfully updated",
            }

            return make_response(jsonify(response_data), 200)

        else:
            data = jsonify({"error": "Place not found"})
            return make_response(data, 404)

    @jwt_required()
    def get(self, id):
        # Retrieve a single place by id
        place = PlaceModel.objects(id=id).first()
        if place:

            data = jsonify(place)
            return make_response(data, 200)

        else:
            data = jsonify({"error": "Place not found"})
            return make_response(data, 404)

    @jwt_required()
    def delete(self, id):
        # Delete a place
        place = PlaceModel.objects(id=id).delete()
        if place:

            data = jsonify({"success": True})
            return make_response(data, 200)
        else:
            data = jsonify({"error": "Place not found"})
            return make_response(data, 404)


@blp.route("/green/insert")
class InsertGreenSpot(MethodView):

    @blp.arguments(InsertGreenSchema)
    @jwt_required()
    def post(self, place_data):
        for place in place_data["spot_names"]:
            if not GreenDictModel.objects(spot_name=place).first():  # Avoid duplicates
                new_spot = GreenDictModel(spot_name=place)
                new_spot.save()
        data = jsonify({"message": "green spot insert to mongo db successfully"})
        return make_response(data, 201)
