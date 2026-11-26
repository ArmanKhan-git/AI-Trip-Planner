import time

import requests
from config import EXCHANGE_RATE_API_KEY


BASE_URL = "https://v6.exchangerate-api.com/v6"

_CACHE_TTL_SECONDS = 60 * 60
_cache = {"rates": None, "fetched_at": 0.0}


def _usd_rates() -> dict:
    """USD-based conversion table, cached for an hour."""

    now = time.time()

    if _cache["rates"] is None or now - _cache["fetched_at"] > _CACHE_TTL_SECONDS:
        response = requests.get(
            f"{BASE_URL}/{EXCHANGE_RATE_API_KEY}/latest/USD",
            timeout=10,
        )
        response.raise_for_status()
        _cache["rates"] = response.json()["conversion_rates"]
        _cache["fetched_at"] = now

    return _cache["rates"]


def get_usd_rate(currency: str) -> float:
    """How many units of `currency` one USD buys."""

    return _usd_rates()[currency.upper()]


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    rates = _usd_rates()
    return amount / rates[from_currency.upper()] * rates[to_currency.upper()]


def get_usd_to_inr_rate() -> float:
    return get_usd_rate("INR")
