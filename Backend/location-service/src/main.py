import asyncio

from database.data_interface import MongoDB
from config.config import TRAVELDB_URL
from domain.suggestion_service import SuggestionService
from interface.grpc_handlers import LocationServiceHandler
from infra.grpc_server import serve

if __name__ == "__main__":
  travel_db = MongoDB(TRAVELDB_URL, database="travel_db", collection="location_plus")
  travel_vector_db = MongoDB(TRAVELDB_URL, database="travel_db", collection="locations_vector_plus")
  handler = LocationServiceHandler(SuggestionService(travel_db, travel_vector_db))
  asyncio.run(serve(handler))

