from db import mongo as mg


class PlaceModel(mg.Document):
    placename = mg.StringField()
    openingTime = mg.StringField()
    address = mg.StringField()
    long = mg.StringField()
    lat = mg.StringField()
    rating = mg.FloatField()
    lowCarbon = mg.BooleanField()
    image = mg.StringField()
