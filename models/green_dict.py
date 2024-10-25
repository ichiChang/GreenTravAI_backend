from db import mongo as mg


class GreenDictModel(mg.Document):
    spot_name = mg.StringField(required=True, unique=True)

    meta = {
        'indexes': [
            'spot_name'  
        ]
    }
