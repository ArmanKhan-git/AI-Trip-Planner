from graph.state import TripState


def route_start(state: TripState):
    if state.get("prefilled"):
        return "completeness_checker"
    return "trip_extractor"


def route_trip(state: TripState):
    if state["trip_complete"]:
        return "flight_agent"
    else:
        return "ask_user"
