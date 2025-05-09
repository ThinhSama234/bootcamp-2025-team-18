from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from marshmallow import ValidationError

from models.schemas import ImportRequestSchema, BatchImportRequestSchema
from services.import_service import ImportService

logger = logging.getLogger(__name__)

import_bp = Blueprint('import_bp', __name__)

import_service = ImportService()
import_schema = ImportRequestSchema()
batch_import_schema = BatchImportRequestSchema()

@import_bp.route('/')
def root():
  return jsonify({"message": "Import API Service is running"})

@import_bp.route('/api/v1/import', methods=['POST'])
def import_data():
  try:
    data = import_schema.load(request.json)
    logger.info(f"Processing import request from source: {data['source']}")
    
    request_id = import_service.send_to_kafka(
      source=data['source'],
      data=data['data'],
      metadata=data.get('metadata')
    )
    
    return jsonify({
      "status": "success",
      "message": "Data sent to processing queue",
      "timestamp": datetime.now().isoformat(),
      "request_id": request_id
    }), 200
    
  except ValidationError as e:
    logger.warning(f"Validation error in import request: {e.messages}")
    return jsonify({
      "status": "error",
      "message": "Validation failed",
      "errors": e.messages
    }), 400
  except Exception as e:
    logger.error(f"Error processing import request: {str(e)}")
    return jsonify({
      "status": "error",
      "message": str(e)
    }), 500

@import_bp.route('/api/v1/import/batch', methods=['POST'])
def batch_import():
  try:
    data = batch_import_schema.load(request.json)
    logger.info(f"Processing batch import request from source: {data['source']} with {len(data['items'])} items")
    
    batch_id = import_service.batch_send_to_kafka(
      source=data['source'],
      items=data['items'],
      metadata=data.get('metadata')
    )
    
    return jsonify({
      "status": "success",
      "message": f"Batch import initiated with {len(data['items'])} items",
      "timestamp": datetime.now().isoformat(),
      "request_id": batch_id
    }), 200
    
  except ValidationError as e:
    logger.warning(f"Validation error in batch import request: {e.messages}")
    return jsonify({
      "status": "error",
      "message": "Validation failed",
      "errors": e.messages
    }), 400
  except Exception as e:
    logger.error(f"Error processing batch import request: {str(e)}")
    return jsonify({
      "status": "error",
      "message": str(e)
    }), 500