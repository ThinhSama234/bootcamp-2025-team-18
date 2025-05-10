import os
from flask import Flask
from flask_cors import CORS
import logging
from dotenv import load_dotenv
load_dotenv()

from routes import register_routes 

PORT = int(os.getenv('PORT', 8000))

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

register_routes(app)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=PORT)