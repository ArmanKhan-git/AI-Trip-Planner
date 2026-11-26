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
        "places.userRatingCount,"
        "places.priceLevel,"
        "places.priceRange"
    ),
}

# PRICE_LEVEL_MODERATE -> "$$"
PRICE_LEVELS = {
    "PRICE_LEVEL_FREE": "Free",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}


def _format_price_range(price_range: dict):
    """{'startPrice': {'currencyCode': 'JPY', 'units': '3000'}, 'endPrice': {...}} -> 'JPY 3000-5000'"""

    if not price_range:
        return None

    start = price_range.get("startPrice") or {}
    end = price_range.get("endPrice") or {}
    currency = start.get("currencyCode") or end.get("currencyCode") or ""

    if start.get("units") and end.get("units"):
        return f"{currency} {start['units']}-{end['units']}"
    if start.get("units"):
        return f"{currency} {start['units']}+"
    return None


def search_places(city: str, place_type: str, limit: int = 5):

    payload = {
        "textQuery": f"{place_type} in {city}",
        "pageSize": min(limit, 20),
    }

    response = requests.post(
        URL,
        headers=HEADERS,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    places = response.json().get("places", [])

    results = []

    for place in places:

        result = {
            "name": place["displayName"]["text"],
            "address": place.get("formattedAddress"),
            "rating": place.get("rating"),
            "reviews": place.get("userRatingCount"),
        }

        price_level = PRICE_LEVELS.get(place.get("priceLevel"))
        if price_level:
            result["price_level"] = price_level

        price_range = _format_price_range(place.get("priceRange"))
        if price_range:
            result["price_range_per_person"] = price_range

        results.append(result)

    return results[:limit]
