from datetime import datetime
from graph.state import TripState


def date_calculator(state: TripState):

    departure = state.get("departure_date")
    returning = state.get("return_date")

    if departure and returning:

        departure = datetime.strptime(
            departure,
            "%Y-%m-%d"
        )

        returning = datetime.strptime(
            returning,
            "%Y-%m-%d"
        )

        days = (returning - departure).days

        return {
            "days": days
        }

    return {}