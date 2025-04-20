from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/from-data-service', methods=['POST'])
def from_data_service():
    data = request.json
    print(f"[LocationService] Received from Data Service: {data}")
    return jsonify({'status': 'received from data service'})

@app.route('/from-backend', methods=['POST'])
def from_nodejs():
    data = request.json
    print(f"[LocationService] Received from Node.js: {data}")
    return jsonify({'status': 'received from Node.js'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
