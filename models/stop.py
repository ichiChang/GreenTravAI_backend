from db import mongo as mg
from models.day import DayModel
from models.place import PlaceModel
from models.travelPlan import TravelPlanModel


class StopModel(mg.Document):
    Name = mg.StringField(required=True)
    StartTime = mg.DateTimeField()
    EndTime = mg.DateTimeField()
    note = mg.StringField()
    transportation = mg.DictField()
    PlaceId = mg.ReferenceField(document_type=PlaceModel)
    DayId = mg.ReferenceField(document_type=DayModel)
    address = mg.StringField()
    prev_stopId = mg.StringField(null=True, required=False)
    Isgreen = mg.BooleanField()
    coordinates = mg.PointField()

    # TravelPlan_id = mg.ReferenceField(document_type=TravelPlanModel)
