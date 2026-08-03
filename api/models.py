from pydantic import BaseModel


class TripRequest(BaseModel):
    prompt: str