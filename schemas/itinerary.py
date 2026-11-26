from pydantic import BaseModel, Field
from typing import List, Optional


# ----------------------------
# Trip Summary
# ----------------------------

class TripSummary(BaseModel):
    destination: str
    departure_city: str
    departure_date: str
    return_date: str
    travelers: int
    budget: float
    currency: str


# ----------------------------
# Flight
# ----------------------------

class FlightLeg(BaseModel):
    from_code: str
    to_code: str
    departure: str
    arrival: str
    duration: str
    stops: int


class Flight(BaseModel):
    offer_id: str = Field(description="The `id` of the chosen offer from LIVE FLIGHT OPTIONS, copied exactly.")
    airline: str
    airline_code: str
    price_usd: float = Field(description="Round-trip price per traveler in the offer's original currency.")
    price: float = Field(description="Round-trip price per traveler in the trip currency.")
    duration: str = Field(description="Outbound flight duration.")
    stops: int = Field(description="Outbound stops.")
    reason: str
    # Filled in by code from live Duffel data; leave null.
    outbound: Optional[FlightLeg] = None
    return_leg: Optional[FlightLeg] = None


# ----------------------------
# Hotel
# ----------------------------

class Hotel(BaseModel):
    name: str
    rating: float
    reviews: int
    estimated_nightly_cost: float
    estimated_total_cost: float
    reason: str

class TripStatus(BaseModel):
    is_affordable: bool
    status: str
    budget_difference: float

# ----------------------------
# Budget
# ----------------------------

class Budget(BaseModel):
    flights: float
    hotel: float
    food: float
    transport: float
    miscellaneous: float

    total: float
    remaining: float

    confidence: str
    flight_percent: float
    hotel_percent: float
    food_percent: float
    transport_percent: float
    miscellaneous_percent: float

# ----------------------------
# Flight Comparison
# ----------------------------

class FlightComparison(BaseModel):
    offer_id: str = Field(description="The `id` of this offer from LIVE FLIGHT OPTIONS, copied exactly.")
    airline: str
    price: float = Field(description="Round-trip price per traveler in the trip currency.")
    duration: str
    stops: int
    pros: str
    cons: str
    # Filled in by code from live Duffel data; leave null.
    outbound: Optional[FlightLeg] = None
    return_leg: Optional[FlightLeg] = None


# ----------------------------
# Hotel Comparison
# ----------------------------

class HotelComparison(BaseModel):
    name: str
    rating: float
    estimated_cost: float
    pros: str
    cons: str


# ----------------------------
# Restaurant
# ----------------------------

class Restaurant(BaseModel):
    name: str
    cuisine: str
    price_range: str

    average_cost_per_person: float

    distance_km: float

    rating: float

    reason: str

    # Computed in code: how much this pick saves vs. the day's other dinner option.
    estimated_saving: float = 0

    # Set in code: Google's per-person price range used to validate the cost, e.g. "THB 200-400".
    google_price_range: Optional[str] = None

    # Set in code: the price is Google's minimum for an open-ended range ("JPY 10000+"), shown as "from ₹X".
    price_is_minimum: bool = False


# ----------------------------
# Day Plan
# ----------------------------

class Day(BaseModel):
    day: int

    morning: str

    afternoon: str

    evening: str

    restaurant: Restaurant = Field(
        description="Recommended DINNER: a well-reviewed, reputable mid-range ($$-$$$) restaurant."
    )

    # Required so the model cannot silently skip it; code sets it to None when it
    # duplicates `restaurant` (travel days with no evening at the destination).
    fine_dining: Optional[Restaurant] = Field(
        ...,
        description="Fine-dining ($$$$) DINNER alternative for the same evening; same as `restaurant` on pure travel days."
    )

    # Computed in code from the trip dates, e.g. "2026-11-28".
    date: Optional[str] = None

    # Computed in code from flight times: no dinner at the destination on this day.
    travel_day: bool = False

    # Set when exporting: "fine" if the user swapped in the fine-dining option for this day.
    dinner_choice: Optional[str] = None

    breakfast_lunch_allowance: float = Field(
        default=0,
        description="Typical cost PER PERSON for breakfast + lunch at convenience stores, cafes or casual local spots, in the trip currency."
    )

    # Computed in code: recommended dinner + breakfast/lunch allowance, per person.
    daily_food_cost_per_person: float = 0

    attractions: List[str]


# ----------------------------
# Money Saving Tip
# ----------------------------

class SavingTip(BaseModel):
    tip: str
    estimated_saving: float

#----------------------------
#Restaurant comparison
#----------------------------
class RestaurantComparison(BaseModel):
    name: str
    cuisine: str
    price_range: str
    average_cost_per_person: float
    estimated_total_cost: float
    pros: str
    cons: str


# ----------------------------
# Confidence
# ----------------------------

class Confidence(BaseModel):
    flight: str
    hotel: str
    food: str
    transport: str
    miscellaneous: str
    overall: str

# ----------------------------
# Summary
# ----------------------------
class Summary(BaseModel):

    destination: str

    departure_city: str

    departure_date: str

    return_date: str

    travelers: int

    days: int

    total_budget: float

    estimated_trip_cost: float

    remaining_budget: float

    status: str


# ----------------------------
# Final Output
# ----------------------------

class Itinerary(BaseModel):

    summary: Summary

    trip_summary: TripSummary

    selected_flight: Flight

    selected_hotel: Hotel

    budget: Budget

    flight_comparison: List[FlightComparison]

    hotel_comparison: List[HotelComparison]

    restaurant_comparison: List[RestaurantComparison]

    itinerary: List[Day]

    money_saving_tips: List[SavingTip]

    travel_tips: List[str]

    trip_status: TripStatus


    confidence: Confidence

# ----------------------------
# Regenerated day plan (after the user picks another flight/hotel)
# ----------------------------

class DayPlan(BaseModel):
    itinerary: List[Day]
