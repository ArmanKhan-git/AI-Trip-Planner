from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

from schemas.itinerary import Itinerary


class TripState(TypedDict, total=False):
    destination_city: Optional[str]
    departure_city: Optional[str]
    days: Optional[int]
    nights: Optional[int]
    budget: Optional[float]
    currency: Optional[str]
    travelers: Optional[int]
    departure_date: Optional[str]
    return_date: Optional[str]
    # True when the caller (the API form) already supplied every trip field,
    # so the LLM extractor can be skipped.
    prefilled: Optional[bool]
    flights: Optional[list]
    hotels: Optional[list]
    places: Optional[list]
    restaurants: Optional[list]
    itinerary: Optional[str]
    trip_complete: bool
    final_itinerary: Optional[Itinerary]
    messages: Annotated[list, add_messages]
