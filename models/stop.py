from db import mongo as mg
from models.day import DayModel
from models.place import PlaceModel


class StopModel(mg.Document):
    Name = mg.StringField(required=True)
    StartTime = mg.DateTimeField()
    EndTime = mg.DateTimeField()
    note = mg.StringField()
    PlaceId = mg.ReferenceField(document_type=PlaceModel)
    DayId = mg.ReferenceField(document_type=DayModel)
