from pydantic import BaseModel
from typing import List


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

class Flight(BaseModel):
    airline: str
    airline_code: str
    price_usd: float
    price_inr: float
    duration: str
    stops: int
    reason: str


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
    airline: str
    price: float
    duration: str
    stops: int
    pros: str
    cons: str


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

    estimated_saving: float


# ----------------------------
# Day Plan
# ----------------------------

class Day(BaseModel):
    day: int

    morning: str

    afternoon: str

    evening: str

    restaurant: Restaurant

    nearby_restaurants: List[Restaurant]

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