from schemas.itinerary import Summary


def create_summary(itinerary):

    return Summary(

        destination=itinerary.trip_summary.destination,

        departure_city=itinerary.trip_summary.departure_city,

        departure_date=itinerary.trip_summary.departure_date,

        return_date=itinerary.trip_summary.return_date,

        travelers=itinerary.trip_summary.travelers,

        days=len(itinerary.itinerary),

        total_budget=itinerary.trip_summary.budget,

        estimated_trip_cost=itinerary.budget.total,

        remaining_budget=itinerary.budget.remaining,

        status=itinerary.trip_status.status
    )