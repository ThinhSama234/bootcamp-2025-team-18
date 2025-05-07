from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from typing import Dict, Any

# class LocationSchema(Schema):
#   name = fields.Str(required=True, validate=validate.Length(min=1))
#   description = fields.Str(required=True, validate=validate.Length(min=10))
#   address = fields.Str(required=True)
#   coordinates = fields.Dict(keys=fields.Str(), values=fields.Float(), required=True)
#   category = fields.Str(required=False)
#   images = fields.List(fields.Str(), required=False)

class ImportRequestSchema(Schema):
  source = fields.Str(required=True)
  data = fields.Dict(required=True)
  metadata = fields.Dict()

  @validates_schema
  def validate_data(self, data: Dict[str, Any], **kwargs):
    if not data['source']:
      raise ValidationError('Source field cannot be empty')
    if not data['data']:
      raise ValidationError('Data field cannot be empty')
    if not isinstance(data['data'], dict):
      raise ValidationError('Data field must be a JSON object')

class BatchImportRequestSchema(Schema):
  source = fields.Str(required=True)
  items = fields.List(fields.Dict(), required=True)
  metadata = fields.Dict()

  @validates_schema
  def validate_items(self, data: Dict[str, Any], **kwargs):
    if not data['source']:
      raise ValidationError('Source field cannot be empty')
    if not data['items']:
      raise ValidationError('Items list cannot be empty')
    for item in data['items']:
      if not isinstance(item, dict):
        raise ValidationError('Each item must be a JSON object')