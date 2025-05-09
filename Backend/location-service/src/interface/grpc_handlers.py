from generated import location_service_pb2 as pb2
from generated import location_service_pb2_grpc as pb2_grpc

class LocationServiceHandler(pb2_grpc.SuggestionServicer):
  def __init__(self, suggestion_service):
    self.suggestion_service = suggestion_service

  def GetSuggestions(self, request, context):
    id = self.suggestion_service.get_session_id()
    yield pb2.SuggestionReply(type="INIT", content=id)

    location_ids = self.suggestion_service.get_location_ids(request.k, request.messages, request.image_urls)
    for location_id in location_ids:
      description = self.suggestion_service.get_location_response(location_id)
      yield pb2.SuggestionReply(type="SUGGESTION", content=description)
  
