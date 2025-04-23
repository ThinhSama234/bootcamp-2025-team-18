from flask import Flask, request, jsonify, Blueprint

def create_routes():
  bp = Blueprint("main", __name__)

  @bp.route('/from-data-service', methods=['POST'])
  def from_data_service():
    data = request.json
    print(f"[LocationService] Received from Data Service: {data}")
    return jsonify({'status': 'received from data service'})

  @bp.route('/from-backend', methods=['POST'])
  def from_nodejs():
    data = request.json
    print(f"[LocationService] Received from Node.js: {data}")
    return jsonify({'status': 'received from Node.js'})
  return bp
