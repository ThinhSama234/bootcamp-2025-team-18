from flask import Flask
from interface.flask_routes import create_routes
from dotenv import load_dotenv
import os

def create_flask_app():
    app = Flask(__name__)
    app.register_blueprint(create_routes())
    return app

def run_flask(app):
    load_dotenv()
    PORT = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=PORT)
