from marshmallow import Schema, fields

class LocationSchema(Schema):
  """ Location data model """
  name = fields.Str(required=True)
  address = fields.Str(required=True)
  description = fields.Str(required=True)
  category = fields.Str(allow_none=True)

  latitude = fields.Str(allow_none=True)
  longitude = fields.Str(allow_none=True)
  image_url = fields.List(fields.Str(), default=[])

class MessageSchema(Schema):
  batch_id = fields.Str(allow_none=True)
  request_id = fields.Str(allow_none=True)
  source = fields.Str(required=True)
  type = fields.Str(required=True)
  data = fields.Nested(LocationSchema, required=True)
  metadata = fields.Dict(allow_none=True)  

