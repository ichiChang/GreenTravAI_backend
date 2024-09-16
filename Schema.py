from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(UserSchema):
    username = fields.Str(required=True)


class AddTravelPlanSchema(Schema):
    planname = fields.Str(required=True, validate=validate.Length(min=1))
    startdate = fields.Date(required=True, format='%Y-%m-%d') #date
    enddate = fields.Date(required=True, format='%Y-%m-%d') #date


class UpdateTravelPlanSchema(Schema):
    planname = fields.Str(validate=validate.Length(min=1))
    startdate = fields.Date( format='%Y-%m-%d') #date
    enddate = fields.Date( format='%Y-%m-%d') #date
    id = fields.Str(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(min=1))
    StartDay = fields.Date(required=True, format='%Y-%m-%d') #date
    EndDay = fields.Date(required=True, format='%Y-%m-%d') #date
    CreateAt = fields.DateTime(dump_only=True)
    # UserId = fields.Str(required=True, load_only=True)


class PlaceSchema(Schema):
    placename = fields.Str()
    openingTime = fields.Str()
    address = fields.Str()
    long = fields.Str()
    lat = fields.Str()
    rating = fields.Float()
    lowCarbon = fields.Raw(type="boolean")
    image = fields.Raw(type="file", description="Upload image", required=False)


class StopSchema(Schema):
    id = fields.Str(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(min=1))
    StartTime = fields.DateTime(format='%Y-%m-%d %H:%M', required=False) #time
    EndTime = fields.DateTime(format='%Y-%m-%d %H:%M', required=False) #time
    note = fields.Str()
    PlaceId = fields.Str(required=True)
    DayId = fields.Str(required=True)
    


class AddStopSchema(StopSchema):
    isContinue = fields.Boolean()
    latency = fields.Int()
    prev_stop = fields.Str(allow_none=True)

class LinkStopSchema(Schema):
    origin_Sid = fields.Str(required=True)
    dest_Sid = fields.Str(required=True)

class StopinDaySchema(Schema):
    day_id = fields.Str(required=True)

class EditStopIndSchema(Schema):
    stop_id = fields.String(required=True)            # Individual stop_id
    previous_stop_id = fields.String(required=True, allow_none=True)   # Individual previous_stop_id

class EditStopSchema(Schema):
    stops = fields.List(fields.Nested(EditStopIndSchema), required=True)  # List of stop objects




class UpdateStopSchema(Schema):
    Name = fields.Str(validate=validate.Length(min=1))
    StartTime = fields.DateTime(format='%Y-%m-%d %H:%M') #time
    EndTime = fields.DateTime(format='%Y-%m-%d %H:%M') #time
    note = fields.Str()
    PlaceId = fields.Str()
    DayId = fields.Str()


class TransportationSchema(Schema):
    id = fields.Str(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(min=1))
    TimeSpent = fields.Int(required=True)
    LowCarbon = fields.Boolean()
    CreateAt = fields.DateTime(dump_only=True)
    FromStopId = fields.Str(required=True)
    ToStopId = fields.Str(required=True)


class AddTransportationSchema(TransportationSchema):
    pass


class UpdateTransportationSchema(Schema):
    Name = fields.Str(validate=validate.Length(min=1))
    TimeSpent = fields.Int()
    LowCarbon = fields.Boolean()
    FromStopId = fields.Str()
    ToStopId = fields.Str()


class DaySchema(Schema):
    id = fields.Str(dump_only=True)
    Date = fields.Date(required=True, format='%Y-%m-%d') #date
    #date_time = fields.DateTime(format='%Y-%m-%d %H:%M') #time
    TravelPlanId = fields.Str(required=True)


class AddDaySchema(DaySchema):
    pass

class DayinPlanSchema(Schema):
    TravelPlanId = fields.Str(required=True)


class UpdateDaySchema(Schema):
    Date = fields.Date(required=True, format='%Y-%m-%d') #time
    # TravelPlanId = fields.Str(required=True)

class ChatbotSchema(Schema):
    query = fields.Str(required=True)
