from typing import TypedDict, Annotated,Optional
from langgraph.graph.message import add_messages

from schemas.itinerary import Itinerary

class TripState(TypedDict):
    destination_city: Optional[str]
    departure_city: Optional[str]
    days: Optional[int]
    budget: Optional[float]
    travelers: Optional[int]
    departure_date:Optional[str]
    return_date:Optional[str]
    flights: Optional[list]
    hotels: Optional[list]
    places: Optional[list]
    restaurants: Optional[list]
    itinerary: Optional[str]
    trip_complete: bool
    final_itinerary: Optional[Itinerary]
    messages: Annotated[list, add_messages]
