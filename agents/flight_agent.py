from graph.state import TripState
from langchain_core.messages import AIMessage

from tools.airport_lookup import get_airport_code
from tools.flights import search_flights


def flight_agent(state: TripState):

    departure_code = get_airport_code(state["departure_city"])
    destination_code = get_airport_code(state["destination_city"])

    flights = search_flights(
        departure_code=departure_code,
        destination_code=destination_code,
        departure_date=state["departure_date"],
        return_date=state["return_date"],
    )

    if not flights:
        return {
            "flights": [],
            "messages": [
                AIMessage(
                    content="Sorry, I couldn't find any flights for those dates."
                )
            ]
        }

    return {
        "flights": flights,
        "messages": [
            AIMessage(
                content=f"Found {len(flights)} flight options."
                
            )
        ]
    }