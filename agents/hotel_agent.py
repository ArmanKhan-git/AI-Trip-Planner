from graph.state import TripState
from langchain_core.messages import AIMessage
from tools.places import search_places


def hotel_agent(state: TripState):

    hotels = search_places(
        city=state["destination_city"],
        place_type="hotel"
    )

    return {
        "hotels": hotels,
        "messages": [
            AIMessage(
                content=f"Found {len(hotels)} hotels."
            )
        ]
    }