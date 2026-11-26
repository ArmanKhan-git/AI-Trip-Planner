from graph.state import TripState
from langchain_core.messages import AIMessage
from tools.places import search_places


def restaurant_agent(state: TripState):

    city = state["destination_city"]

    # Everyday dinner candidates across all price tiers.
    popular = search_places(city=city, place_type="popular local restaurants", limit=20)

    # Dedicated high-end search: the popular list rarely has enough $$$$ places
    # to give every evening a genuine fine-dining alternative.
    fine = search_places(city=city, place_type="fine dining restaurants", limit=10)

    restaurants = []
    seen = set()
    for tier, results in (("everyday", popular), ("fine_dining_candidate", fine)):
        for r in results:
            key = r["name"].lower()
            if key in seen:
                continue
            seen.add(key)
            restaurants.append({**r, "search": tier})

    return {
        "restaurants": restaurants,
        "messages": [
            AIMessage(
                content=f"Found {len(restaurants)} restaurants."
            )
        ]
    }
