from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from graph.graph import graph
from api.models import TripRequest

router = APIRouter()


@router.post("/plan")
def plan_trip(request: TripRequest):
    try:
        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=request.prompt)
                ]
            },
            config={
                "configurable": {
                    "thread_id": "api-session"
                }
            }
        )

        # Trip is incomplete
        if not result.get("trip_complete", False):
            return {
                "success": False,
                "needs_more_info": True,
                "message": result["messages"][-1].content
            }

        # Trip is complete
        itinerary = result["final_itinerary"]

        return {
            "success": True,
            "needs_more_info": False,
            "message": "Itinerary generated successfully.",
            "data": itinerary.model_dump()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trip generation failed: {str(e)}"
        )