"""
Deterministic clean-up of LLM-generated days, shared by the full itinerary
agent and the /itinerary (regenerate) endpoint.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional

from schemas.itinerary import Day
from tools.exchange_rate import convert

# "THB 200-400" (bounded) or "THB 2000+" (open-ended top tier), as built in tools/places.py
_PRICE_RANGE = re.compile(r"^([A-Z]{3})\s+(\d+)(?:-(\d+)|\+)$")

# Google's top bucket only gives a minimum ("THB 2000+"); real high-end prices sit well above it.
OPEN_ENDED_FLOOR_MULTIPLIER = 1.5


def _norm(name: str) -> str:
    return " ".join((name or "").lower().split())


def _parse(ts: str):
    try:
        return datetime.strptime(ts[:16], "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError):
        return None


def flight_timing_notes(outbound: dict, return_leg: dict, departure_date: str) -> dict:
    """
    Plain-language timing facts so the model doesn't have to do date arithmetic.
    Legs are dicts with `departure` / `arrival` ISO timestamps (airport-local time).
    """

    notes = {}
    try:
        day1 = datetime.strptime(departure_date, "%Y-%m-%d")
    except (TypeError, ValueError):
        return notes

    def day_no(dt):
        return (dt.date() - day1.date()).days + 1

    arr = _parse((outbound or {}).get("arrival"))
    if arr:
        n = day_no(arr)
        note = f"Lands {arr:%d %b} at {arr:%H:%M} (Day {n})."
        if n > 1:
            note += f" Day 1 is a travel day; check-in happens on Day {n}."
        if arr.hour < 6:
            note += f" Arrival is in the early hours, so keep Day {n} morning light."
        notes["arrival_note"] = note

    dep = _parse((return_leg or {}).get("departure"))
    if dep:
        n = day_no(dep)
        leave = dep - timedelta(hours=3)
        note = f"Return flight departs {dep:%d %b} at {dep:%H:%M} (Day {n}). Leave the hotel by about {leave:%H:%M}"
        # Leaving before ~06:00 means the traveler goes to the airport during the previous night.
        if leave.date() < dep.date() or leave.hour < 6:
            note += f" on the night of Day {n - 1}: Day {n - 1}'s evening ends with the airport transfer, and Day {n} is only the flight home."
        else:
            note += f" on Day {n}."
        notes["return_note"] = note

    return notes


def scrub_computed_fields(days: List[Day]):
    """
    Reset fields that only code may set. The model can see them in the schema and
    sometimes fills them in (e.g. marking every price as a minimum).
    """
    for day in days:
        day.date = None
        day.travel_day = False
        day.dinner_choice = None
        day.daily_food_cost_per_person = 0
        for r in (day.restaurant, day.fine_dining):
            if r:
                r.price_is_minimum = False
                r.google_price_range = None
                r.estimated_saving = 0


def _tier_from_range(obj):
    """The model sometimes copies Google's range ("JPY 10000+") into the $–$$$$ tier field."""
    match = _PRICE_RANGE.match((obj.price_range or "").strip())
    if match:
        obj.price_range = "$$$" if match.group(3) else "$$$$"


def travel_days_without_dinner(outbound: dict, return_leg: dict, departure_date: str) -> set:
    """
    Day numbers on which the traveler can't have dinner at the destination:
    - every day before the outbound flight lands (overnight flights)
    - the return day, if they must leave for the airport before ~19:00
    """

    result = set()
    try:
        day1 = datetime.strptime(departure_date, "%Y-%m-%d")
    except (TypeError, ValueError):
        return result

    def day_no(dt):
        return (dt.date() - day1.date()).days + 1

    arr = _parse((outbound or {}).get("arrival"))
    if arr:
        result.update(range(1, day_no(arr)))

    dep = _parse((return_leg or {}).get("departure"))
    if dep:
        leave = dep - timedelta(hours=3)
        if leave.date() < dep.date() or leave.hour < 19:
            result.add(day_no(dep))

    return result


def finalize_days(days: List[Day], departure_date: str, no_dinner_days: Optional[set] = None) -> float:
    """
    - stamps each day with its calendar date
    - drops `fine_dining` when it just repeats the recommended dinner
    - marks travel days (no dinner at the destination) and leaves dinner out of their food cost
    - computes the per-day food cost and "saves X vs fine dining"
    - removes attraction tags already used on an earlier day

    Returns total food cost PER PERSON for the whole trip.
    """

    start = None
    try:
        start = datetime.strptime(departure_date, "%Y-%m-%d")
    except (TypeError, ValueError):
        pass

    days.sort(key=lambda d: d.day)

    seen_attractions = set()
    total_per_person = 0.0

    # Breakfast/lunch still happen on travel days; if the model left the allowance at 0,
    # use ~80% of the typical allowance from the other days.
    no_dinner_days = no_dinner_days or set()
    normal = [d.breakfast_lunch_allowance for d in days if d.day not in no_dinner_days and d.breakfast_lunch_allowance > 0]
    typical = sorted(normal)[len(normal) // 2] if normal else 0
    for d in days:
        if d.breakfast_lunch_allowance <= 0 and typical:
            d.breakfast_lunch_allowance = round(typical * 0.8, -1)

    for day in days:
        if start:
            day.date = (start + timedelta(days=day.day - 1)).strftime("%Y-%m-%d")

        dinner = day.restaurant
        fine = day.fine_dining
        for r in (dinner, fine):
            if r:
                _tier_from_range(r)

        day.travel_day = day.day in no_dinner_days
        if day.travel_day:
            day.fine_dining = None
            fine = None

        if fine and (
            _norm(fine.name) == _norm(dinner.name)
            or fine.average_cost_per_person <= dinner.average_cost_per_person
        ):
            day.fine_dining = None
            fine = None

        dinner.estimated_saving = (
            round(fine.average_cost_per_person - dinner.average_cost_per_person, 2) if fine else 0
        )
        if fine:
            fine.estimated_saving = 0

        dinner_cost = 0 if day.travel_day else dinner.average_cost_per_person
        day.daily_food_cost_per_person = round(dinner_cost + day.breakfast_lunch_allowance, 2)
        total_per_person += day.daily_food_cost_per_person

        unique = []
        for attraction in day.attractions:
            key = _norm(attraction)
            if key and key not in seen_attractions:
                seen_attractions.add(key)
                unique.append(attraction)
        day.attractions = unique

    return total_per_person


# ----------------------------------------------------------------------
# Google price-range check
# ----------------------------------------------------------------------

def _find_range(name: str, ranges: dict) -> Optional[str]:
    key = _norm(name)
    if key in ranges:
        return ranges[key]
    # Tolerate small naming differences ("NOBU Tokyo" vs "Nobu Tokyo Toranomon").
    for known, text in ranges.items():
        if len(key) >= 5 and len(known) >= 5 and (key in known or known in key):
            return text
    return None


def _range_bounds(range_text: str, currency: str):
    """'THB 200-400' -> (low, high) and 'THB 2000+' -> (low, None), converted to `currency`."""

    match = _PRICE_RANGE.match(range_text or "")
    if not match:
        return None
    local_currency, low, high = match.group(1), float(match.group(2)), match.group(3)
    try:
        return (
            convert(low, local_currency, currency),
            convert(float(high), local_currency, currency) if high else None,
        )
    except KeyError:
        return None


def _nice(amount: float, currency: str) -> float:
    return round(amount, -1) if currency == "INR" else round(amount)


def apply_price_ranges(days: List[Day], comparison: list, restaurants: list, currency: str, travelers: int):
    """
    Validate LLM restaurant prices against Google's per-person price ranges (in place).

      bounded range ("THB 200-400"): keep the estimate if inside, otherwise use the midpoint
      open-ended ("THB 2000+"):      Google only gives a minimum. Estimates below 1.5x that minimum
                                     are shifted up together so the cheapest meets it, keeping the
                                     AI's differences between restaurants (no identical prices).
    """

    # Price tier ($ … $$$$) always comes from Google when known, not from the model.
    levels = {_norm(r["name"]): r["price_level"] for r in restaurants or [] if r.get("price_level")}

    def tier(obj):
        level = _find_range(obj.name, levels)
        if level:
            obj.price_range = level
        else:
            _tier_from_range(obj)

    for day in days:
        for r in (day.restaurant, day.fine_dining):
            if r:
                tier(r)
    for rc in comparison or []:
        tier(rc)

    ranges = {
        _norm(r["name"]): r["price_range_per_person"]
        for r in restaurants or []
        if r.get("price_range_per_person")
    }
    if not ranges:
        return

    # (object, cost attribute) pairs to check
    items = []
    for day in days:
        for r in (day.restaurant, day.fine_dining):
            if r:
                r.google_price_range = _find_range(r.name, ranges)
                items.append(r)
    items.extend(comparison or [])

    open_ended = {}  # floor -> [objects below it]

    for obj in items:
        text = _find_range(obj.name, ranges)
        bounds = _range_bounds(text, currency) if text else None
        if not bounds:
            continue
        low, high = bounds
        cost = obj.average_cost_per_person

        if high is not None:
            if not (low <= cost <= high):
                obj.average_cost_per_person = _nice((low + high) / 2, currency)
        else:
            floor = low * OPEN_ENDED_FLOOR_MULTIPLIER
            if cost < floor:
                open_ended.setdefault(floor, []).append(obj)

    for floor, below in open_ended.items():
        shift = floor - min(o.average_cost_per_person for o in below)
        for o in below:
            o.average_cost_per_person = _nice(o.average_cost_per_person + shift, currency)
            if hasattr(o, "price_is_minimum"):
                # Google only gives a minimum here, so present it honestly as "from ₹X".
                o.price_is_minimum = True

    for rc in comparison or []:
        rc.estimated_total_cost = round(rc.average_cost_per_person * travelers, 2)


def local_currency_hint(restaurants: list, currency: str) -> str:
    """
    "1 JPY = ₹0.58" style line so the model converts local menu prices directly
    instead of thinking in round USD amounts.
    """

    for r in restaurants or []:
        match = _PRICE_RANGE.match(r.get("price_range_per_person") or "")
        if match and match.group(1) != currency:
            local = match.group(1)
            try:
                return f"1 {local} = {convert(1, local, currency):.4f} {currency}"
            except KeyError:
                return ""
    return ""
