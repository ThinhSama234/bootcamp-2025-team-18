import os

from dotenv import load_dotenv
from grpc import aio
from generated.location_service_pb2_grpc import add_SuggestionServicer_to_server

async def serve(location_handler):
  server = aio.server()
  add_SuggestionServicer_to_server(location_handler, server)
  
  load_dotenv()
  PORT = int(os.getenv("GRPC_PORT", 50051))
  server.add_insecure_port(f'[::]:{PORT}')
  print(f"gRPC server started on port {PORT}")
  await server.start()
  await server.wait_for_termination()
