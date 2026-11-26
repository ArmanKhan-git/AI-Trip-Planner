from models.model import llm
from prompts.itinerary_prompt import day_plan_prompt
from schemas.itinerary import DayPlan
from tools.exchange_rate import get_usd_rate
from utils.day_plan import finalize_days, apply_price_ranges, travel_days_without_dinner, scrub_computed_fields
from utils.trip_dates import nights_and_days


structured_llm = llm.with_structured_output(DayPlan)


def _norm(name: str) -> str:
    return " ".join((name or "").lower().split())


def regenerate_days(trip: dict, flight: dict, hotel: dict, restaurants: list, places: list,
                    known_prices: dict = None):
    """
    Re-plan only the day-by-day itinerary for a user-chosen flight and hotel.
    No flight/places API calls: the restaurant and attraction lists come from the first response.
    """

    currency = trip.get("currency") or "INR"
    nights, days = nights_and_days(trip["departure_date"], trip["return_date"])

    prompt = day_plan_prompt(
        trip=trip,
        flight=flight,
        hotel=hotel,
        restaurants=restaurants,
        places=places,
        exchange_rate=get_usd_rate(currency),
        nights=nights,
        days=days,
        currency_code=currency,
    )

    plan = structured_llm.invoke(prompt)
    scrub_computed_fields(plan.itinerary)

    # Same restaurant, same price as in the original plan (consistency + no copy-pasted estimates).
    known = {_norm(k): v for k, v in (known_prices or {}).items() if v}
    for day in plan.itinerary:
        for r in (day.restaurant, day.fine_dining):
            if r and _norm(r.name) in known:
                r.average_cost_per_person = known[_norm(r.name)]
    apply_price_ranges(plan.itinerary, [], restaurants, currency, trip.get("travelers") or 1)
    no_dinner = travel_days_without_dinner(flight.get("outbound"), flight.get("return_leg"), trip["departure_date"])
    finalize_days(plan.itinerary, trip["departure_date"], no_dinner)

    return plan.itinerary
