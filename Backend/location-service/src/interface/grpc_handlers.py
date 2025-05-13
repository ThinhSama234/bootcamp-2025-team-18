from generated import location_service_pb2 as pb2
from generated import location_service_pb2_grpc as pb2_grpc
from domain.suggestion_service import SuggestionService

class LocationServiceHandler(pb2_grpc.SuggestionServicer):
  def __init__(self, suggestion_service: SuggestionService):
    self.suggestion_service = suggestion_service

  def GetSuggestions(self, request, context):
    suggestion_id = self.suggestion_service.get_session_id()
    yield pb2.SuggestionReply(type="INIT", rank=-1, content=suggestion_id)

    location_ids = self.suggestion_service.get_location_ids(request.k, request.messages, request.image_urls, request.coordinates)
    for i, location_id in enumerate(location_ids):
      description = self.suggestion_service.get_location_response(request.messages, location_id)
      yield pb2.SuggestionReply(type="SUGGESTION", rank=i+1, content=description)
  
