from db import mongo as mg
from models.place import PlaceModel
from models.user import UserModel


class favorPlaceModel(mg.Document):
    UserId = mg.ReferenceField(document_type=UserModel)
    PlaceId = mg.StringField()
    is_deleted = mg.BooleanField()
