from graph.state import TripState
from langchain_core.messages import AIMessage
from tools.places import search_places


def places_agent(state: TripState):

    places = search_places(
        city=state["destination_city"],
        place_type="tourist attraction"
    )

    return {
        "places": places,
        "messages": [
            AIMessage(
                content=f"Found {len(places)} attractions."
            )
        ]
    }