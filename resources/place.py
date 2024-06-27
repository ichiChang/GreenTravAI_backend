# resources/place.py
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from models.place import PlaceModel
from Schema import PlaceSchema
from services.google_storage import upload_image_to_gcs
from werkzeug.utils import secure_filename

blp = Blueprint('places', 'places', url_prefix='/places')

@blp.route('/')
class Places(MethodView):

    def get(self):
        # Retrieve all places
        places = PlaceModel.objects()
        return jsonify(places), 200

    @blp.arguments(PlaceSchema)
    def post(self, new_data):
        # Create a new place with validated data
        image = request.files.get('image')
        if image:
            filename = secure_filename(image.filename)
            image_url = upload_image_to_gcs(image.read(), filename, image.content_type)
            new_data['Image'] = image_url
        place = PlaceModel(**new_data).save()
        return jsonify(place), 201

@blp.route('/<string:id>')
class Place(MethodView):

    @blp.arguments(PlaceSchema)
    def put(self, update_data, id):
        # Update a place with validated data
        image = request.files.get('image')
        place = PlaceModel.objects(id=id).first()
        if place:
            if image:
                filename = secure_filename(image.filename)
                image_url = upload_image_to_gcs(image.read(), filename, image.content_type)
                update_data['Image'] = image_url
            place.update(**update_data)
            return jsonify(place), 200
        else:
            return jsonify(error='Place not found'), 404

    def get(self, id):
        # Retrieve a single place by id
        place = PlaceModel.objects(id=id).first()
        if place:
            return jsonify(place), 200
        else:
            return jsonify(error='Place not found'), 404

    def delete(self, id):
        # Delete a place
        place = PlaceModel.objects(id=id).delete()
        if place:
            return jsonify(success=True), 200
        else:
            return jsonify(error='Place not found'), 404