import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from langchain_core.messages import HumanMessage

from graph.graph import graph
from api.models import TripRequest, RegenerateRequest, PdfRequest
from utils.pdf_export import apply_selections
from utils.pdfs.pdf_generator import build_pdf
from agents.day_plan_agent import regenerate_days
from tools.airport_lookup import get_airport_code
from utils.trip_dates import nights_and_days

router = APIRouter()


@router.post("/plan")
def plan_trip(request: TripRequest):

    for city in (request.departure_city, request.destination_city):
        if not get_airport_code(city):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported city: {city}"
            )

    nights, days = nights_and_days(request.departure_date, request.return_date)

    prompt = request.prompt or (
        f"Plan a trip from {request.departure_city} to {request.destination_city} "
        f"for {request.travelers} traveler(s) from {request.departure_date} "
        f"to {request.return_date} with a budget of {request.budget} {request.currency}."
    )

    initial_state = {
        "departure_city": request.departure_city,
        "destination_city": request.destination_city,
        "departure_date": request.departure_date.isoformat(),
        "return_date": request.return_date.isoformat(),
        "travelers": request.travelers,
        "budget": request.budget,
        "currency": request.currency,
        "nights": nights,
        "days": days,
        "prefilled": True,
        "messages": [HumanMessage(content=prompt)],
    }

    try:
        result = graph.invoke(initial_state)

        if not result.get("final_itinerary"):
            return {
                "success": False,
                "needs_more_info": not result.get("trip_complete", False),
                "message": result["messages"][-1].content
            }

        itinerary = result["final_itinerary"]

        return {
            "success": True,
            "needs_more_info": False,
            "message": "Itinerary generated successfully.",
            "data": itinerary.model_dump(),
            # Raw lists the frontend sends back to /itinerary when the user changes flight/hotel.
            "context": {
                "restaurants": result.get("restaurants") or [],
                "places": result.get("places") or [],
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trip generation failed: {str(e)}"
        )


@router.post("/itinerary")
def regenerate_itinerary(request: RegenerateRequest):
    trip = {
        "departure_city": request.departure_city,
        "destination_city": request.destination_city,
        "departure_date": request.departure_date.isoformat(),
        "return_date": request.return_date.isoformat(),
        "travelers": request.travelers,
        "currency": request.currency,
    }

    try:
        days = regenerate_days(
            trip=trip,
            flight=request.flight.model_dump(),
            hotel=request.hotel.model_dump(),
            restaurants=request.restaurants,
            places=request.places,
            known_prices=request.known_prices,
        )

        return {
            "success": True,
            "data": {"itinerary": [d.model_dump() for d in days]},
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Itinerary regeneration failed: {str(e)}"
        )


@router.post("/pdf")
def download_pdf(request: PdfRequest):
    original = request.itinerary
    flight_changed = bool(request.flight_offer_id) and request.flight_offer_id != original.selected_flight.offer_id
    hotel_changed = bool(request.hotel_name) and request.hotel_name.strip().lower() != original.selected_hotel.name.strip().lower()

    try:
        itinerary = apply_selections(
            original,
            flight_offer_id=request.flight_offer_id,
            hotel_name=request.hotel_name,
            fine_dining_days=request.fine_dining_days,
        )
        pdf_bytes = build_pdf(
            itinerary,
            flight_pick="YOUR PICK" if flight_changed else "AI PICK",
            hotel_pick="YOUR PICK" if hotel_changed else "AI PICK",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

    # e.g. "Delhi_to_Tokyo_8_Days_Plan.pdf"
    trip = itinerary.trip_summary
    days = len(itinerary.itinerary)

    def slug(text):
        return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_") or "Trip"

    filename = f"{slug(trip.departure_city)}_to_{slug(trip.destination)}_{days}_Day{'s' if days != 1 else ''}_Plan.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
