from graph.state import TripState
from langchain_core.messages import AIMessage

from prompts.itinerary_prompt import itinerary_prompt
from models.model import llm
from schemas.itinerary import Itinerary

from tools.exchange_rate import get_usd_to_inr_rate

from utils.pdfs.pdf_generator import save_pdf
from utils.terminal_renderer import render_itinerary
from utils.formatter import format_duration
from utils.budget import calculate_budget_percentages
from utils.trip_status import calculate_trip_status
from utils.summary import create_summary



rate = get_usd_to_inr_rate()

structured_llm = llm.with_structured_output(Itinerary)



def itinerary_agent(state: TripState):

    prompt = itinerary_prompt(
        state,
        exchange_rate=rate
    )

    response = structured_llm.invoke(prompt)
    response.selected_flight.duration = format_duration(
    response.selected_flight.duration
)
    response.budget = calculate_budget_percentages(
    response.budget
)
    response.trip_status = calculate_trip_status(
    response.budget
)
    response.summary = create_summary(response)
    
    # Beautiful terminal output
    render_itinerary(response)


    return {
        "final_itinerary": response,
        "messages": [
            AIMessage(
                content="✅ Itinerary generated successfully!"
            )
        ]
    }