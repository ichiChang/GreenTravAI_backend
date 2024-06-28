# resources/place.py
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from models.place import PlaceModel
from Schema import PlaceSchema
from services.google_storage import upload_image_to_gcs
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
import traceback

blp = Blueprint("places", __name__, url_prefix="/places")


@blp.route("/")
class Places(MethodView):

    @jwt_required()
    def get(self):
        # Retrieve all places
        places = PlaceModel.objects()
        return jsonify(places), 200

    @blp.arguments(PlaceSchema, location="files")
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
            return {
                "message": f'Place named {request.form.get("placename")} created successfully'
            }, 201
        except Exception as e:
            # 打印异常到控制台
            traceback.print_exc()
            # 返回错误信息给客户端
            return {"error": str(e)}, 400


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
