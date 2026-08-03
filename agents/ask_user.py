from graph import state
from graph.state import TripState
from langchain_core.messages import AIMessage

def ask_user(state: TripState):
    missing_info = []
    if not state.get("budget"):
        missing_info.append("budget")

    if not state.get("travelers"):
        missing_info.append("number of travelers")

    if not state.get("departure_city"):
        missing_info.append("departure city")

    if not state.get("destination_city"):
        missing_info.append("destination city")

    if not state.get("departure_date"):
        missing_info.append("departure date")

    if not state.get("return_date"):
        missing_info.append("return date")
        
    return {
        "messages": [
            AIMessage(
                content=f"I need a little more information. Please provide your {', '.join(missing_info)}."
            )
        ]
    }
    