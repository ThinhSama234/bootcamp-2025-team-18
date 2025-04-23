from generated import location_service_pb2 as pb2
from generated import location_service_pb2_grpc as pb2_grpc

class LocationServiceHandler(pb2_grpc.SuggestionServicer):
  def __init__(self, suggestion_service):
    self.suggestion_service = suggestion_service

  def InitSuggestionRequest(self, request, context):
    id = self.suggestion_service.init_suggestion_request(request.group_name, request.k, request.messages)
    return pb2.InitReply(suggestionId=id)
  
  def GetSingleSuggestion(self, request, context):
    suggestion = self.suggestion_service.get_single_suggestion(request.suggestionId)
    return pb2.SuggestionReply(suggestion=suggestion)
