import requests
from config import DUFFEL_API_KEY

BASE_URL = "https://api.duffel.com"

HEADERS = {
    "Authorization": f"Bearer {DUFFEL_API_KEY}",
    "Duffel-Version": "v2",
    "Content-Type": "application/json",
}


def search_flights(
    departure_code: str,
    destination_code: str,
    departure_date: str,
    return_date: str,
    travelers: int,
):
    payload = {
        "data": {
            "slices": [
                {
                    "origin": departure_code,
                    "destination": destination_code,
                    "departure_date": departure_date,
                },
                {
                    "origin": destination_code,
                    "destination": departure_code,
                    "departure_date": return_date,
                },
            ],
            "passengers": [
                {"type": "adult"} for _ in range(travelers)
            ],
            "cabin_class": "economy",
        }
    }

    response = requests.post(
        f"{BASE_URL}/air/offer_requests",
        headers=HEADERS,
        json=payload,
    )

    response.raise_for_status()

    offers = response.json()["data"]["offers"]

    flights = []

    for offer in offers:

        outbound = offer["slices"][0]
        inbound = offer["slices"][1]

        outbound_segment = outbound["segments"][0]
        return_segment = inbound["segments"][0]

        flights.append({
            "id": offer["id"],

            "airline": offer["owner"]["name"],
            "airline_code": offer["owner"]["iata_code"],

            "price": float(offer["total_amount"]),
            "currency": offer["total_currency"],

            "outbound": {
                "from": outbound["origin"]["iata_code"],
                "to": outbound["destination"]["iata_code"],
                "departure": outbound_segment["departing_at"],
                "arrival": outbound_segment["arriving_at"],
                "duration": outbound["duration"],
                "stops": len(outbound["segments"]) - 1,
            },

            "return": {
                "from": inbound["origin"]["iata_code"],
                "to": inbound["destination"]["iata_code"],
                "departure": return_segment["departing_at"],
                "arrival": return_segment["arriving_at"],
                "duration": inbound["duration"],
                "stops": len(inbound["segments"]) - 1,
            },
        })

    flights.sort(key=lambda x: x["price"])
    

    return flights[:5]
