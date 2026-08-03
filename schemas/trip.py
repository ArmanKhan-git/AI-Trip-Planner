from pydantic import BaseModel
from typing import Optional


class ExtractedTrip(BaseModel):
    destination_city: Optional[str] = None
    departure_city: Optional[str] = None

    departure_date: Optional[str] = None
    return_date: Optional[str] = None

    days: Optional[int] = None
    budget: Optional[float] = None
    travelers: Optional[int] = None