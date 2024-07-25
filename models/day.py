from db import mongo as mg
from models.travelPlan import TravelPlanModel


class DayModel(mg.Document):
    Date = mg.DateTimeField(required=True)
    TravelPlanId = mg.ReferenceField(document_type=TravelPlanModel,dbref = False)
