from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)


class AddTravelPlanSchema(Schema):
    planname = fields.Str(required=True, validate=validate.Length(min=1))
    startdate = fields.DateTime(required=True)
    enddate = fields.DateTime(required=True)


class UpdateTravelPlanSchema(Schema):
    planname = fields.Str(validate=validate.Length(min=1))
    startdate = fields.DateTime()
    enddate = fields.DateTime()
    id = fields.Str(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(min=1))
    StartDay = fields.DateTime(required=True)
    EndDay = fields.DateTime(required=True)
    CreateAt = fields.DateTime(dump_only=True)
    UserId = fields.Str(required=True, load_only=True)


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
    StartTime = fields.DateTime()
    EndTime = fields.DateTime()
    note = fields.Str()
    PlaceId = fields.Str(required=True)
    DayId = fields.Str(required=True)


class AddStopSchema(StopSchema):
    pass


class UpdateStopSchema(Schema):
    Name = fields.Str(validate=validate.Length(min=1))
    StartTime = fields.DateTime()
    EndTime = fields.DateTime()
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
    Date = fields.DateTime(required=True)
    TravelPlanId = fields.Str(required=True)


class AddDaySchema(DaySchema):
    pass


class UpdateDaySchema(Schema):
    Date = fields.DateTime()
    TravelPlanId = fields.Str()
