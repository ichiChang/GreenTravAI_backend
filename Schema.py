from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(UserSchema):
    username = fields.Str(required=True)


class AddTravelPlanSchema(Schema):
    planname = fields.Str(required=True, validate=validate.Length(min=1))
    startdate = fields.Date(required=True, format="%Y-%m-%d")  # date
    enddate = fields.Date(required=True, format="%Y-%m-%d")  # date


class UpdateTravelPlanSchema(Schema):
    planname = fields.Str(validate=validate.Length(min=1))
    startdate = fields.Date(format="%Y-%m-%d")  # date
    enddate = fields.Date(format="%Y-%m-%d")  # date
    id = fields.Str(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(min=1))
    StartDay = fields.Date(required=True, format="%Y-%m-%d")  # date
    EndDay = fields.Date(required=True, format="%Y-%m-%d")  # date
    CreateAt = fields.DateTime(dump_only=True)
    # UserId = fields.Str(required=True, load_only=True)


from marshmallow import Schema, fields


class CreateAllStopSchema(Schema):
    Location = fields.Str()
    description = fields.Str()
    latency = fields.Int()
    Address = fields.Str()
    Activity = fields.Str()
    # StartTime = fields.DateTime(
    #     format="%Y-%m-%d %H:%M", required=False, example="2024-09-17 08:00"
    # )


class CreateDaySchema(Schema):
    # stops = fields.List(fields.Nested(CreateAllStopSchema), required=True)
    Recommendation = fields.List(fields.Nested(CreateAllStopSchema), required=True)


class CreateAllSchema(Schema):
    startdate = fields.Date(format="%Y-%m-%d")  # date
    enddate = fields.Date(format="%Y-%m-%d")  # date
    planname = fields.Str()
    # days = fields.List(fields.Nested(CreateDaySchema), required=True)
    Plans = fields.List(fields.Nested(CreateDaySchema), required=True)




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
    StartTime = fields.DateTime(
        format="%Y-%m-%d %H:%M", required=False, example="2024-09-17 08:00"
    )  # time
    # EndTime = fields.DateTime(format='%Y-%m-%d %H:%M', required=False,example="2024-09-17 08:00") #time
    note = fields.Str()
    # PlaceId = fields.Str(required=True)
    DayId = fields.Str(required=True)


class AddStopSchema(StopSchema):
    # isContinue = fields.Boolean()
    latency = fields.Int()
    address = fields.Str(required=True)
    prev_stop = fields.Str(allow_none=True)


class LinkStopSchema(Schema):
    origin_Sid = fields.Str(required=True)
    dest_Sid = fields.Str(required=True)


class StopinDaySchema(Schema):
    day_id = fields.Str(required=True)


class EditStopIndSchema(Schema):
    stop_id = fields.String(required=True)  # Individual stop_id
    previous_stop_id = fields.String(
        required=True, allow_none=True
    )  # Individual previous_stop_id


class EditStopSchema(Schema):
    stops = fields.List(
        fields.Nested(EditStopIndSchema), required=True
    )  # List of stop objects


class UpdateStopSchema(Schema):
    Name = fields.Str(validate=validate.Length(min=1), required=False, allow_none=True)
    note = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)
    latency = fields.Int(required=False, allow_none=True)


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


class ChooseTransportationSchema(Schema):
    FromStopId = fields.Str(required=True)
    ToStopId = fields.Str(required=True)


class ChooseTransportationUpdateSchema(Schema):
    FromStopId = fields.Str(required=True)
    mode = fields.Str(required=True)
    TimeSpent = fields.Int(required=True)


class UpdateTransportationSchema(Schema):
    Name = fields.Str(validate=validate.Length(min=1))
    TimeSpent = fields.Int()
    LowCarbon = fields.Boolean()
    FromStopId = fields.Str()
    ToStopId = fields.Str()


class DaySchema(Schema):
    id = fields.Str(dump_only=True)
    Date = fields.Date(required=True, format="%Y-%m-%d")  # date
    # date_time = fields.DateTime(format='%Y-%m-%d %H:%M') #time
    TravelPlanId = fields.Str(required=True)


class AddDaySchema(DaySchema):
    pass


class DayinPlanSchema(Schema):
    TravelPlanId = fields.Str(required=True)


class UpdateDaySchema(Schema):
    Date = fields.Date(required=True, format="%Y-%m-%d")  # time
    # TravelPlanId = fields.Str(required=True)


class ChatbotSchema(Schema):
    query = fields.Str(required=True)


class FavorPlaceSchema(Schema):
    UserId = fields.Str(required=True)
    PlaceId = fields.Str(required=True)


class RetrieveFavorPlaceSchema(Schema):
    UserId = fields.Str(required=True)


class InsertGreenSchema(Schema):
    spot_names = fields.List(fields.String(), required=True)
