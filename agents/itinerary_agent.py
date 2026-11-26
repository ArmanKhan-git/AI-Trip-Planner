from graph.state import TripState
from langchain_core.messages import AIMessage

from prompts.itinerary_prompt import itinerary_prompt
from models.model import llm
from schemas.itinerary import Itinerary, FlightLeg

from tools.exchange_rate import get_usd_rate, convert

from utils.terminal_renderer import render_itinerary
from utils.formatter import format_duration
from utils.budget import calculate_budget_percentages
from utils.trip_status import calculate_trip_status
from utils.summary import create_summary
from utils.trip_dates import nights_and_days
from utils.day_plan import finalize_days, apply_price_ranges, travel_days_without_dinner, scrub_computed_fields


structured_llm = llm.with_structured_output(Itinerary)


def _leg(raw: dict) -> FlightLeg:
    return FlightLeg(
        from_code=raw["from"],
        to_code=raw["to"],
        departure=raw["departure"],
        arrival=raw["arrival"],
        duration=format_duration(raw["duration"]),
        stops=raw["stops"],
    )


def _apply_live_flight(target, offer: dict, currency: str):
    """Overwrite LLM-written flight facts with the real Duffel offer."""

    target.airline = offer["airline"]
    target.price = round(convert(offer["price"], offer["currency"], currency), 2)
    target.outbound = _leg(offer["outbound"])
    target.return_leg = _leg(offer["return"])
    target.duration = target.outbound.duration
    target.stops = target.outbound.stops


def _enrich_flights(response: Itinerary, flights: list, currency: str):
    offers = {f["id"]: f for f in flights or []}

    selected = response.selected_flight
    offer = offers.get(selected.offer_id)
    if offer:
        _apply_live_flight(selected, offer, currency)
        selected.airline_code = offer["airline_code"]
        selected.price_usd = offer["price"]
    else:
        selected.duration = format_duration(selected.duration)

    for fc in response.flight_comparison:
        offer = offers.get(fc.offer_id)
        if offer:
            _apply_live_flight(fc, offer, currency)
        else:
            fc.duration = format_duration(fc.duration)


def _norm(name: str) -> str:
    return " ".join((name or "").lower().split())


def _dedupe_comparisons(response: Itinerary):
    """Comparison lists must not repeat the selected option or list anything twice."""

    seen = {response.selected_flight.offer_id}
    flights = []
    for fc in response.flight_comparison:
        if fc.offer_id not in seen:
            seen.add(fc.offer_id)
            flights.append(fc)
    response.flight_comparison = flights

    seen = {_norm(response.selected_hotel.name)}
    hotels = []
    for hc in response.hotel_comparison:
        if _norm(hc.name) not in seen:
            seen.add(_norm(hc.name))
            hotels.append(hc)
    response.hotel_comparison = hotels


def _set_confidence(response: Itinerary, state: TripState, flight_matched: bool):
    """Confidence reflects where each number came from, not the model's self-assessment."""

    has_price_data = any("price_level" in r for r in state.get("restaurants") or [])

    c = response.confidence
    c.flight = "High" if flight_matched else "Low"            # live Duffel offer vs. LLM guess
    c.hotel = "Medium" if state.get("hotels") else "Low"      # real hotel, LLM-estimated rate
    c.food = "Medium" if has_price_data else "Low"            # Places price tiers vs. pure estimate
    c.transport = "Medium"                                    # LLM estimate of transit costs
    c.miscellaneous = "Medium"                                # LLM-estimated buffer

    rank = {"Low": 0, "Medium": 1, "High": 2}
    c.overall = min([c.flight, c.hotel, c.food, c.transport, c.miscellaneous], key=rank.get)


def _recalculate_budget(response: Itinerary, budget: float, travelers: int, nights: int):
    hotel = response.selected_hotel
    hotel.estimated_total_cost = round(hotel.estimated_nightly_cost * nights, 2)

    b = response.budget
    b.flights = round(response.selected_flight.price * travelers, 2)
    b.hotel = hotel.estimated_total_cost
    b.total = round(b.flights + b.hotel + b.food + b.transport + b.miscellaneous, 2)
    b.remaining = round(budget - b.total, 2)


def itinerary_agent(state: TripState):

    currency = state.get("currency") or "INR"
    travelers = state.get("travelers") or 1

    computed = nights_and_days(state.get("departure_date"), state.get("return_date"))
    if computed:
        nights, days = computed
    else:
        days = state.get("days") or 1
        nights = max(days - 1, 1)

    rate = get_usd_rate(currency)

    prompt = itinerary_prompt(
        state,
        exchange_rate=rate,
        nights=nights,
        days=days,
        currency_code=currency,
    )

    response = structured_llm.invoke(prompt)
    scrub_computed_fields(response.itinerary)

    response.trip_summary.currency = currency
    response.trip_summary.travelers = travelers
    response.trip_summary.budget = state.get("budget") or response.trip_summary.budget

    flight_matched = any(
        f["id"] == response.selected_flight.offer_id for f in state.get("flights") or []
    )
    _enrich_flights(response, state.get("flights"), currency)
    _dedupe_comparisons(response)

    apply_price_ranges(
        response.itinerary, response.restaurant_comparison,
        state.get("restaurants"), currency, travelers,
    )
    sf = response.selected_flight
    no_dinner = travel_days_without_dinner(
        sf.outbound.model_dump() if sf.outbound else None,
        sf.return_leg.model_dump() if sf.return_leg else None,
        state.get("departure_date"),
    )
    food_per_person = finalize_days(response.itinerary, state.get("departure_date"), no_dinner)
    if food_per_person > 0:
        response.budget.food = round(food_per_person * travelers, 2)
    _recalculate_budget(response, response.trip_summary.budget, travelers, nights)

    response.budget = calculate_budget_percentages(response.budget)
    response.trip_status = calculate_trip_status(response.budget)
    response.summary = create_summary(response)
    _set_confidence(response, state, flight_matched)

    # Beautiful terminal output
    render_itinerary(response)

    return {
        "final_itinerary": response,
        "messages": [
            AIMessage(
                content="✅ Itinerary generated successfully!"
            )
        ]
    }
