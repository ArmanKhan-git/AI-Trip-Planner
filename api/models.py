from datetime import date
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from schemas.itinerary import Itinerary


class TripRequest(BaseModel):
    departure_city: str
    destination_city: str
    departure_date: date
    return_date: date
    travelers: int = Field(1, ge=1, le=9)
    budget: float = Field(gt=0)
    currency: Literal["INR", "USD"] = "INR"

    # Human-readable summary the frontend builds; only used as the
    # conversation's first message (e.g. for LangSmith traces).
    prompt: Optional[str] = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.return_date <= self.departure_date:
            raise ValueError("return_date must be after departure_date")
        return self


class ChosenFlight(BaseModel):
    airline: str
    outbound: Optional[Dict[str, Any]] = None
    return_leg: Optional[Dict[str, Any]] = None


class ChosenHotel(BaseModel):
    name: str
    rating: Optional[float] = None


class RegenerateRequest(TripRequest):
    """Re-plan the days for the flight and hotel the user picked."""

    flight: ChosenFlight
    hotel: ChosenHotel
    # Sent back from the /plan response's `context`, so no external APIs are called again.
    restaurants: List[Dict[str, Any]] = []
    places: List[Dict[str, Any]] = []
    # Restaurant name -> per-person price from the first plan, so a restaurant keeps its price.
    known_prices: Dict[str, float] = {}


class PdfRequest(BaseModel):
    """The /plan result (with the current, possibly regenerated, days) plus the user's on-screen choices."""

    itinerary: Itinerary
    flight_offer_id: Optional[str] = None
    hotel_name: Optional[str] = None
    fine_dining_days: List[int] = []
