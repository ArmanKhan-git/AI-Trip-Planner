import requests
from config import EXCHANGE_RATE_API_KEY


BASE_URL = "https://v6.exchangerate-api.com/v6"


def get_usd_to_inr_rate() -> float:

    response = requests.get(
        f"{BASE_URL}/{EXCHANGE_RATE_API_KEY}/latest/USD"
    )

    response.raise_for_status()

    data = response.json()

    return data["conversion_rates"]["INR"]