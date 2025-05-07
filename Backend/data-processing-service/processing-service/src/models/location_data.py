from marshmallow import Schema, fields


class LocationDataSchema(Schema):
  """Schema for validating location data"""
  name = fields.Str(required=True)
  description = fields.Str(allow_none=True)
  address = fields.Str(allow_none=True)
  coordinates = fields.Dict(keys=fields.Str(), values=fields.Float(), allow_none=True)
  source_url = fields.Str(allow_none=True)
  crawled_at = fields.DateTime(allow_none=True)
