from graph.state import TripState
def route_trip(state: TripState):
    if state["trip_complete"]:
        return "flight_agent"
    else:
        return "ask_user"