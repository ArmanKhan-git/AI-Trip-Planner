from graph.state import TripState
from langchain_core.messages import AIMessage
from tools.places import search_places


def restaurant_agent(state: TripState):

    restaurants = search_places(
        city=state["destination_city"],
        place_type="restaurant"
    )

    return {
        "restaurants": restaurants,
        "messages": [
            AIMessage(
                content=f"Found {len(restaurants)} restaurants."
            )
        ]
    }