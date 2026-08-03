from schemas.itinerary import TripStatus


def calculate_trip_status(budget):

    affordable = budget.remaining >= 0

    return TripStatus(
        is_affordable=affordable,
        status="Affordable" if affordable else "Over Budget",
        budget_difference=abs(budget.remaining)
    )