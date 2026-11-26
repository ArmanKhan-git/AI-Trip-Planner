import json

from utils.day_plan import flight_timing_notes, local_currency_hint

CURRENCY_SYMBOLS = {"INR": "₹", "USD": "$"}


def _money(amount_usd, exchange_rate, symbol):
    return f"{symbol}{round(amount_usd * exchange_rate, -1 if exchange_rate < 20 else -2):,.0f}"


def _symbol(currency_code):
    return CURRENCY_SYMBOLS.get(currency_code, currency_code + " ")


def day_planning_rules(state, exchange_rate, days, currency_code, flight_ref, restaurants=None):
    """
    Rules shared by the full itinerary prompt and the regenerate-days prompt.
    `flight_ref` tells the model which flight to plan around.
    """

    symbol = _symbol(currency_code)
    meals_low = _money(8, exchange_rate, symbol)
    meals_high = _money(15, exchange_rate, symbol)

    hint = local_currency_hint(restaurants, currency_code)
    local_rate_line = (
        f"   • Local menu prices: {hint}. Convert each restaurant's `price_range_per_person` with THIS rate.\n"
        if hint else ""
    )

    return f"""
=====================================================================
DAY STRUCTURE & FLIGHT TIMES
=====================================================================
   • There are exactly {days} days. Day 1 is {state.get("departure_date")} and Day {days} is {state.get("return_date")};
     each day is one calendar date.
   • Plan around {flight_ref}. Its `arrival_note` and `return_note` were computed in code from the real
     flight times — follow them EXACTLY (they say which day is a travel day and when to leave the hotel).
   • If the outbound flight lands on a LATER date than Day 1 (overnight flight), Day 1 is a travel day:
     describe leaving {state.get("departure_city")}, the flight and the arrival. No sightseeing before arrival.
   • If the traveler lands late at night or before ~06:00, check-in happens on arrival and the next morning should be light.
   • If the return flight departs between 00:00 and ~09:00, the traveler leaves the hotel the PREVIOUS evening
     (~3 hours before departure for international flights): say so in the previous day's evening, and keep
     Day {days} to the flight and arrival only.
   • Never schedule activities that conflict with flight times.

=====================================================================
DAILY DINNER (TWO OPTIONS PER DAY)
=====================================================================
   Dinner is the proper sit-down meal of the day. For EVERY day provide two dinner options near that day's evening plan:
   • `restaurant` — RECOMMENDED dinner: a reputable, well-reviewed MID-RANGE restaurant ($$ to $$$),
     preferably rating ≥ 4.2 with many reviews. This is what a typical traveler would book for a good dinner.
     It is the default used in the food budget.
     NEVER use a $$$$ restaurant as the recommended option.
   • `fine_dining` — FINE-DINING alternative: a genuinely HIGH-END, celebrated restaurant ($$$$) for travelers who
     want to splurge. It MUST cost clearly more than the recommended option (typically 3× or more) and be provided
     for EVERY day the traveler spends an evening at the destination. A casual or mid-range place is NOT fine dining.
     Pick fine-dining options from restaurants marked `"search": "fine_dining_candidate"` (prefer price_level "$$$$").
   • On a day with no evening at the destination (pure travel day), set `fine_dining` to the SAME restaurant as `restaurant`.
   • Prefer restaurants from AVAILABLE RESTAURANTS. Use `price_level` / `price_range_per_person` when present to place
     each restaurant in the right tier and to estimate `average_cost_per_person` (converted to {currency_code}).
   • Dinner picks must be restaurants — never a hotel from the hotel list.
   • `average_cost_per_person` is the cost of THAT DINNER ONLY for one person, in {currency_code}.
{local_rate_line}   • Estimate every restaurant's price individually from its own price range — different restaurants have
     different prices. Never reuse one number for several restaurants, and don't think in round USD amounts.
   • An open-ended range like "JPY 10000+" is only a MINIMUM. For those restaurants use what you know about
     THAT specific restaurant's typical dinner or tasting-menu price (a celebrated tasting menu can cost several
     times more than an upscale grill). Each fine-dining option should get its own realistic price.
   • Give each option a specific `reason` tied to that day's plan — not a generic justification.

=====================================================================
BREAKFAST & LUNCH
=====================================================================
   • Breakfast and lunch are NOT restaurant picks. For every day set `breakfast_lunch_allowance`: what a normal
     traveler spends PER PERSON on breakfast + lunch at convenience stores, cafes or casual local spots
     (e.g. ~{meals_low} to {meals_high}/day per person, adjusted for the destination's prices), in {currency_code}.
   • Food cost is computed in code as (recommended dinner + breakfast_lunch_allowance) × travelers, summed over all days.

=====================================================================
ATTRACTION AND RESTAURANT VARIETY
=====================================================================
   • Each attraction may appear in the `attractions` list of AT MOST ONE day.
   • Do NOT repeat the same attraction in the morning/afternoon/evening text of different days either; if the
     destination truly has too few, plan a different nearby experience instead.
   • Do NOT repeat the same restaurant across days (applies to both dinner options), unless the restaurant list is
     exhausted — then prefer a different well-known nearby restaurant over a repeat.
   • Before finalizing, review all days: if any attraction or restaurant name appears more than once, replace the
     later occurrence.
"""


def itinerary_prompt(state, exchange_rate, nights, days, currency_code="INR"):

    currency_symbol = _symbol(currency_code)

    transit_low = _money(10, exchange_rate, currency_symbol)
    transit_high = _money(18, exchange_rate, currency_symbol)

    flights = json.dumps(
        [
            {**f, **flight_timing_notes(f.get("outbound"), f.get("return"), state.get("departure_date"))}
            for f in state.get("flights") or []
        ],
        separators=(",", ":"), ensure_ascii=False,
    )
    hotels = json.dumps(state.get("hotels", []), separators=(",", ":"), ensure_ascii=False)
    restaurants = json.dumps(state.get("restaurants", []), separators=(",", ":"), ensure_ascii=False)
    places = json.dumps(state.get("places", []), separators=(",", ":"), ensure_ascii=False)

    shared_rules = day_planning_rules(
        state, exchange_rate, days, currency_code,
        flight_ref="the flight you choose as `selected_flight`",
        restaurants=state.get("restaurants"),
    )

    return f"""
You are Voyage AI, an expert AI Travel Planner and Financial Advisor.

Your primary goal is NOT simply to generate a travel plan. Your primary responsibility is to analyze the financial feasibility of the trip and generate a structured JSON object adhering strictly to the requested schema.

=====================================================================
TRIP DETAILS
=====================================================================
Destination: {state.get("destination_city", "N/A")}
Departure City: {state.get("departure_city", "N/A")}
Departure Date: {state.get("departure_date", "N/A")}
Return Date: {state.get("return_date", "N/A")}
Trip Duration: {days} Days ({nights} Nights)
Travelers: {state.get("travelers", 1)}
Total Budget: {currency_symbol}{state.get("budget", 0)}
Currency: {currency_code}

=====================================================================
LIVE FLIGHT OPTIONS
=====================================================================
{flights}

=====================================================================
AVAILABLE HOTELS
=====================================================================
{hotels}

=====================================================================
AVAILABLE RESTAURANTS
=====================================================================
{restaurants}

=====================================================================
AVAILABLE TOURIST ATTRACTIONS
=====================================================================
{places}

=====================================================================
HANDLING MISSING DATA
=====================================================================
If any of the lists above (flights, hotels, restaurants, places) are empty:
   • Do not invent specific named venues or fabricate real-sounding options.
   • Use realistic, clearly-labeled market-rate estimates instead (e.g. "Estimated based on typical Tokyo mid-range hotel rates").
   • State this limitation plainly in the relevant `reason` field.

=====================================================================
RULES & CALCULATIONS
=====================================================================
Note: numeric totals, percentages, confidence levels and the affordability
decision are recalculated deterministically in code after you respond.
Focus on realistic, well-justified individual estimates.

1. CURRENCY CONVERSION:
   1 USD = {currency_symbol}{exchange_rate:.2f}
   Convert any USD amounts to {currency_code} using ONLY this rate.
   All monetary amounts you output (except `price_usd`) MUST be in {currency_code}.
   Set `trip_summary.currency` to exactly "{currency_code}".

2. FLIGHT PRICING & SELECTION:
   • Live flight prices in the JSON are ROUND-TRIP prices PER TRAVELER (see each offer's `currency`).
   • Copy each offer's `id` EXACTLY into `offer_id` (for `selected_flight` and every `flight_comparison` entry). Do not invent ids.
   • Leave `outbound` and `return_leg` null — they are filled in from live data afterward.
   • Rank flights by: 1) Direct flights (Stops = 0), 2) Lowest total price, 3) Shortest duration.
   • Choose ONE best flight for `selected_flight`. Put every OTHER offer in `flight_comparison` (never repeat the
     selected offer there), each with a genuine, specific pro and con.

3. HOTEL ESTIMATION & SELECTION (PER ROOM):
   • Choose ONE hotel ONLY from the provided list based on rating, review count, and location.
   • Hotel cost is calculated per ROOM (assume 1 shared room for up to 2 travelers).
   • Total Hotel Cost = Estimated Nightly Room Rate × {nights} Nights.
   • Include 2-4 OTHER hotels in `hotel_comparison` — never repeat the selected hotel there, and never list a hotel twice.

4. RESTAURANT COMPARISON:
   • Populate `restaurant_comparison` with 4-6 dining options spanning the full range from $ to $$$$, independent of the daily itinerary picks.
   • Calculate realistic `average_cost_per_person` and `estimated_total_cost` (Cost per person × {state.get("travelers", 1)}) for each.
   • Include specific pros, cons, and note potential savings versus pricier alternatives.

5. OTHER DAILY EXPENSES (MUST SCALE WITH TRAVELERS):
   • Local Transport:
     - Estimate subway/public transit cost PER TRAVELER (e.g. ~{transit_low} to {transit_high}/day per person, adjusted for the destination).
     - Total Transport = (Daily Per-Person Transit × {days} Days) × {state.get("travelers", 1)} Travelers.
   • Miscellaneous:
     - Estimate buffer funds for tickets, entry passes, and incidentals PER TRAVELER.
     - Total Miscellaneous = (Daily Per-Person Buffer × {days} Days) × {state.get("travelers", 1)} Travelers.

6. FEASIBILITY AND ITINERARY GENERATION:
   • Even if the estimated total appears to exceed the budget, generate a complete day-by-day `itinerary` for all
     {days} days — every `Day` fully populated. Note concerns in `reason` fields and money-saving tips instead.
{shared_rules}
=====================================================================
REQUIRED OUTPUT INSTRUCTIONS
=====================================================================
Populate every required field in the JSON structure accurately:
- `summary`: Overview containing destination, departure_city, dates, travelers, and days. Budget figures are recalculated in code.
- `trip_summary`: Baseline parameters input by the user, currency set exactly to "{currency_code}".
- `selected_flight`: Detailed choice and justification.
- `selected_hotel`: Detailed choice and justification.
- `budget`: Your best estimate of each category's cost.
- `flight_comparison`: Specific, genuine pros and cons for every other flight option.
- `hotel_comparison`: Specific, genuine pros and cons for other candidate hotels.
- `restaurant_comparison`: Dining analysis across price ranges ($ to $$$$).
- `itinerary`: Full day-by-day plan for every day of the trip.
- `money_saving_tips`: 3-5 actionable tips with estimated saving figures in {currency_symbol}.
- `travel_tips`: Local advice covering weather, transit, SIM/eSIM, currency, etiquette, and safety.
- `trip_status`, `confidence`: Fill with your assessment — both are recalculated in code afterward.
"""


def day_plan_prompt(trip, flight, hotel, restaurants, places, exchange_rate, nights, days, currency_code):
    """Prompt for regenerating only the daily plan after the user picks a different flight or hotel."""

    shared_rules = day_planning_rules(
        trip, exchange_rate, days, currency_code,
        flight_ref="the CHOSEN FLIGHT below",
        restaurants=restaurants,
    )

    return f"""
You are Voyage AI, an expert AI Travel Planner. The traveler has chosen a specific flight and hotel.
Re-plan ONLY the day-by-day itinerary around those choices and return it as `itinerary`.

=====================================================================
TRIP DETAILS
=====================================================================
Destination: {trip.get("destination_city")}
Departure City: {trip.get("departure_city")}
Departure Date: {trip.get("departure_date")}
Return Date: {trip.get("return_date")}
Trip Duration: {days} Days ({nights} Nights)
Travelers: {trip.get("travelers", 1)}
Currency: {currency_code} — every amount you output must be in {currency_code}.

=====================================================================
CHOSEN FLIGHT
=====================================================================
{json.dumps({**flight, **flight_timing_notes(flight.get("outbound"), flight.get("return_leg"), trip.get("departure_date"))}, separators=(",", ":"), ensure_ascii=False)}

=====================================================================
CHOSEN HOTEL (the traveler stays here every night)
=====================================================================
{json.dumps(hotel, separators=(",", ":"), ensure_ascii=False)}
   • Day 1 / arrival must check in at this hotel, and the final day must check out of it.
   • Prefer dinners and evening plans that are reasonably close to this hotel.

=====================================================================
AVAILABLE RESTAURANTS
=====================================================================
{json.dumps(restaurants, separators=(",", ":"), ensure_ascii=False)}

=====================================================================
AVAILABLE TOURIST ATTRACTIONS
=====================================================================
{json.dumps(places, separators=(",", ":"), ensure_ascii=False)}
{shared_rules}
Return all {days} days, fully populated.
"""
