"""
Apply the user's on-screen choices (flight, hotel, dinners) to an itinerary
before rendering it as a PDF, so the download matches what they see.
"""

from typing import List, Optional

from agents.itinerary_agent import _recalculate_budget
from schemas.itinerary import Flight, FlightComparison, Hotel, HotelComparison, Itinerary
from utils.budget import calculate_budget_percentages
from utils.day_plan import finalize_days, travel_days_without_dinner
from utils.summary import create_summary
from utils.trip_dates import nights_and_days
from utils.trip_status import calculate_trip_status


def _norm(name: str) -> str:
    return " ".join((name or "").lower().split())


def _swap_flight(it: Itinerary, offer_id: Optional[str]):
    if not offer_id or offer_id == it.selected_flight.offer_id:
        return
    chosen = next((fc for fc in it.flight_comparison if fc.offer_id == offer_id), None)
    if not chosen:
        return

    old = it.selected_flight
    it.selected_flight = Flight(
        offer_id=chosen.offer_id,
        airline=chosen.airline,
        airline_code="",
        price_usd=0,
        price=chosen.price,
        duration=chosen.duration,
        stops=chosen.stops,
        reason=chosen.pros,
        outbound=chosen.outbound,
        return_leg=chosen.return_leg,
    )
    it.flight_comparison = [
        FlightComparison(
            offer_id=old.offer_id,
            airline=old.airline,
            price=old.price,
            duration=old.duration,
            stops=old.stops,
            pros=f"Original AI pick. {old.reason}",
            cons="",
            outbound=old.outbound,
            return_leg=old.return_leg,
        )
    ] + [fc for fc in it.flight_comparison if fc.offer_id != offer_id]


def _swap_hotel(it: Itinerary, hotel_name: Optional[str], nights: int):
    if not hotel_name or _norm(hotel_name) == _norm(it.selected_hotel.name):
        return
    chosen = next((hc for hc in it.hotel_comparison if _norm(hc.name) == _norm(hotel_name)), None)
    if not chosen:
        return

    old = it.selected_hotel
    it.selected_hotel = Hotel(
        name=chosen.name,
        rating=chosen.rating,
        reviews=0,
        estimated_nightly_cost=round(chosen.estimated_cost / max(nights, 1), 2),
        estimated_total_cost=chosen.estimated_cost,
        reason=chosen.pros,
    )
    it.hotel_comparison = [
        HotelComparison(
            name=old.name,
            rating=old.rating,
            estimated_cost=old.estimated_total_cost,
            pros=f"Original AI pick. {old.reason}",
            cons="",
        )
    ] + [hc for hc in it.hotel_comparison if _norm(hc.name) != _norm(hotel_name)]


def apply_selections(
    it: Itinerary,
    flight_offer_id: Optional[str],
    hotel_name: Optional[str],
    fine_dining_days: List[int],
) -> Itinerary:

    trip = it.trip_summary
    computed = nights_and_days(trip.departure_date, trip.return_date)
    nights = computed[0] if computed else max(len(it.itinerary) - 1, 1)

    _swap_flight(it, flight_offer_id)
    _swap_hotel(it, hotel_name, nights)

    # Days where the user picked fine dining: that becomes the dinner.
    for day in it.itinerary:
        if day.day in fine_dining_days and day.fine_dining:
            day.restaurant, day.fine_dining = day.fine_dining, None
            day.dinner_choice = "fine"

    sf = it.selected_flight
    no_dinner = travel_days_without_dinner(
        sf.outbound.model_dump() if sf.outbound else None,
        sf.return_leg.model_dump() if sf.return_leg else None,
        trip.departure_date,
    )
    food_per_person = finalize_days(it.itinerary, trip.departure_date, no_dinner)
    if food_per_person > 0:
        it.budget.food = round(food_per_person * trip.travelers, 2)

    _recalculate_budget(it, trip.budget, trip.travelers, nights)
    it.budget = calculate_budget_percentages(it.budget)
    it.trip_status = calculate_trip_status(it.budget)
    it.summary = create_summary(it)

    return it
