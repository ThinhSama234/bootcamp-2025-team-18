import uuid

class SuggestionService:
  def get_session_id(self) -> str:
    return str(uuid.uuid4())

  def get_location_ids(self, k: int, messages: list[str]) -> list[str]: # done
    # This is a placeholder implementation. In a real-world scenario, this would involve
    # complex logic to determine the location IDs based on the messages.
    return [str(uuid.uuid4()) for _ in range(k)]
  
  def get_location_description(self, location_id: str) -> str: #???
    # This is a placeholder implementation. In a real-world scenario, this would involve
    # complex logic to determine the location description based on the location ID.
    return f"Description for location {location_id}"
