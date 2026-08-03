from datetime import datetime
from models.model import llm
from schemas.trip import ExtractedTrip
from graph.state import TripState

structured_llm = llm.with_structured_output(ExtractedTrip)


def extractor(state: TripState):
    last_message = state["messages"][-1].content

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
Today's date is {today}.

Extract the user's trip information.

Rules:
- Return dates in YYYY-MM-DD format.
- If the user doesn't specify a year, assume the next upcoming occurrence.
- If information is missing, return null.

User:
{last_message}
"""

    result = structured_llm.invoke(prompt)

    new_data = result.model_dump()

    updated_state = {}

    for key, value in new_data.items():
        if value is not None:
            updated_state[key] = value
        else:
            updated_state[key] = state.get(key)

    return updated_state