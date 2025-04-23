import asyncio
import threading

from domain.suggestion_service import SuggestionService
from interface.grpc_handlers import LocationServiceHandler
from infra.grpc_server import serve
from infra.flask_server import create_flask_app, run_flask

def start_flask():
  app = create_flask_app()
  run_flask(app)

if __name__ == "__main__":
  flask_thread = threading.Thread(target=start_flask)
  flask_thread.start()

  handler = LocationServiceHandler(SuggestionService())
  asyncio.run(serve(handler))

