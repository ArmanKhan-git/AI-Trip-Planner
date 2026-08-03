import requests
from config import GOOGLE_PLACES_API_KEY

URL = "https://places.googleapis.com/v1/places:searchText"

HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
    "X-Goog-FieldMask": (
        "places.displayName,"
        "places.formattedAddress,"
        "places.rating,"
        "places.userRatingCount"
    ),
}


def search_places(city: str, place_type: str):

    payload = {
        "textQuery": f"{place_type} in {city}"
    }

    response = requests.post(
        URL,
        headers=HEADERS,
        json=payload,
    )

    response.raise_for_status()

    places = response.json().get("places", [])

    results = []

    for place in places:

        results.append({

            "name": place["displayName"]["text"],

            "address": place.get("formattedAddress"),

            "rating": place.get("rating"),

            "reviews": place.get("userRatingCount"),
        })

    return results[:5]