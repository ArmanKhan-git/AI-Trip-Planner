from graph.state import TripState

def completeness_checker(state: TripState):

    trip_complete = all([
        state.get("destination_city"),
        state.get("departure_city"),
        state.get("departure_date"),
        state.get("return_date"),
        state.get("travelers"),
        state.get("budget"),
    ])

    return {
        "trip_complete": trip_complete
    }